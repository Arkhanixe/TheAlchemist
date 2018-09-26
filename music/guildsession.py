#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Session implementation. This manages the current player for a given guild.
"""
import asyncio
import copy
import math
import traceback
import weakref
from typing import NoReturn, Union

import async_timeout
import discord
import libneko

from neko2.shared import collections, scribe, string, morefunctools
from . import request

# Allow idle for 10 mins before finishing.
IDLE_TIMEOUT = 10 * 60

# If our ratio of votes exceeds this, then we skip the track.
SKIP_RATIO = 2 / 3

# How long to wait for in seconds between polling the thread for death.
BUSY_WAIT_POLLING_PERIOD = 0.25


# Timeout for banner.
BANNER_TIMEOUT = 5


# Embed to show for banner when not playing anything.
DEFAULT_EMBED = libneko.Embed(
    title="Nothing is in the queue!",
    description="Add something to the queue with n.play.\n\nPlay a playlist with n.mix",
).set_author(name="Up next")


class _WrongChannel(Exception):
    pass


class MusicSessionError(Exception):
    """Error to raise on a music session error occurring."""

    def __init__(self, session, reason):
        self.session = weakref.proxy(session) if session else None
        self.reason = reason

    def __str__(self):
        if isinstance(self.reason, Exception):
            return f"{string.pascal2title(type(self.reason).__name__)} ({str(self.reason)})"
        else:
            return str(self.reason)

    def __repr__(self):
        return f"<{type(self).__qualname__} session={self.session!r} message={self.reason!r}>"

    @classmethod
    def maybe_wrap(cls, session, what):
        """Wraps an element in this class if it is not already wrapped."""
        if isinstance(what, cls):
            return what
        else:
            return MusicSessionError(session, what)


# noinspection PyBroadException
class Session(scribe.Scribe):
    """
    Audio session management wrapper for a given guild.
    """

    @classmethod
    async def new(
        cls,
        loop: asyncio.AbstractEventLoop,
        response_channel: discord.TextChannel,
        voice_channel: discord.VoiceChannel,
        tidy_up: lambda: None,
    ) -> "Session":
        """
        Generate a new session.

        :param loop: the event loop.
        :param response_channel: the channel to send messages to for feedback.
        :param voice_channel: the voice channel to use.
        :param tidy_up: function to tidy up resources on deletion.
        """
        session = None
        try:
            if not (voice_channel.guild and response_channel.guild):
                raise discord.ClientException("Cannot use this in DMs.")

            session = cls(voice_channel, response_channel, loop, tidy_up)
            # We start in skip mode to move the track forward.
            await session._connect()

            return session
        except Exception as ex:
            if session:
                try:
                    session.stop()
                    await session.disconnect()
                except Exception as close_ex:
                    traceback.print_exc(close_ex)
            raise MusicSessionError.maybe_wrap(None, ex) from None

    def __init__(
        self,
        voice_channel: discord.VoiceChannel,
        response_channel: discord.TextChannel,
        loop: asyncio.AbstractEventLoop,
        tidy_up,
    ) -> None:
        """DO NOT CALL THIS DIRECTLY. USE THE ``new`` CLASS METHOD"""
        # Initial voice channel. Currently we reconnect to this if something
        # screws up.
        self._initial_voice_channel = voice_channel

        # Channel to send feedback messages to.
        self.response_channel = response_channel

        # Event loop to schedule on.
        assert loop is not None
        self.loop: asyncio.AbstractEventLoop = weakref.proxy(loop)

        # Voice client being used.
        self.voice_client: discord.VoiceClient = None

        # Track queue.
        self.queue: collections.ObservableAsyncQueue[
            Union[request.Request, request.Mix]
        ] = collections.ObservableAsyncQueue()

        # Current task holding the player
        self._current_player_task: asyncio.Task = None

        # Any logic to invoke on disconnecting.
        self._tidy_up = tidy_up

        # What is currently playing.
        self.now_playing = None

        # Votes to skip
        self.skip_votes = set()

        # Doesn't do anything really...
        self._volume: int = 100

        # Reference to the transformer so we can change the volume.
        self._player: discord.PCMVolumeTransformer = None

        # Now playing banner
        self.banner_task: asyncio.Task = None

    @property
    def voice_channel(self) -> discord.VoiceChannel:
        """Returns the **current** voice channel this session is in."""
        return getattr(self.voice_client, "channel", None)

    @property
    def guild(self) -> discord.Guild:
        return self.voice_channel.guild

    @property
    def is_playing(self) -> bool:
        return self._current_player_task and (
            self.voice_client.is_playing() or self.voice_client.is_paused()
        )

    def __repr__(self) -> str:
        return (
            f"<Session #{id(self)} request={self.now_playing!r} "
            + f"guild={self.guild}#{self.guild.id}>"
        )

    def __len__(self) -> int:
        return len(self.queue)

    def __hash__(self) -> int:
        return hash(self.guild)

    def __raise(self, message) -> NoReturn:
        raise MusicSessionError.maybe_wrap(self, message)

    async def move_to(self, channel):
        """
        Moves us to a new channel. If the channel is a voice channel,
        then we change voice channel. If the channel is a text channel,
        we change the channel we send messages to.
        """
        if isinstance(channel, discord.VoiceChannel):
            await self.voice_client.move_to(channel)
            self._initial_voice_channel = channel
        elif isinstance(channel, discord.TextChannel):
            self.response_channel = channel
        else:
            raise TypeError(
                f"Expected VoiceChannel or TextChannel, not {type(channel).__qualname__}."
            )

    # noinspection PyUnresolvedReferences
    async def _connect(self) -> None:
        if not self.voice_client or not self.voice_client.is_connected():
            if self.voice_client:
                del self.voice_client
            try:
                self.voice_client = await self._initial_voice_channel.connect()
            except Exception as ex:
                self.__raise(ex)

            self._current_player_task = self.loop.create_task(self._player_loop())
        else:
            self.__raise(
                f"Voice client already present in {self._initial_voice_channel.mention}"
            )

    async def _ensure_connected(self) -> None:
        """Ensures we are connected. If we aren't, we reauthorize."""
        if not self.voice_client or not self.voice_client.is_connected():
            await self._connect()

    async def reconnect(self) -> None:
        """Attempt to reconnect to the voice channel."""
        if self.voice_client.is_playing():
            self.stop()

        await self.voice_client.disconnect()
        await self._connect()

    async def disconnect(self) -> None:
        """
        Disconnect from the voice channel. If we are playing anything, that
        will also get cancelled.
        """
        if self.voice_client:
            if self.voice_client.is_playing():
                self.stop()

            await self.voice_client.disconnect()
        del self.voice_client
        self.voice_client = None
        self._tidy_up()

    def stop(self) -> None:
        """Stops the player if it is running."""
        if self.voice_client and self.is_playing:
            self._current_player_task.cancel()

    def skip(self, user) -> None:
        """
        Votes to skip the track.

        Sets the flag event bit to start the next track if more than
        two thirds of listeners have also requested a skip.
        """
        if user not in self.voice_channel.members:
            # Prevents weird voodoo occurring.
            return self.__raise("No one is in the channel.")
        if user in self.skip_votes:
            # Ignore
            return

        self.skip_votes.add(user)

        # Get users in the channel with us.
        members_tot = len(self.voice_channel.members) - 1
        members_vote = len(self.skip_votes)
        critical_ratio = members_tot * SKIP_RATIO
        critical_ratio = int(math.ceil(critical_ratio))

        self.logger.info(
            f"{user} voted to skip in {self} (votes: {members_vote}/{members_tot},"
            f" need at least {critical_ratio} votes to skip)."
        )

        if members_vote >= critical_ratio:
            self.loop.create_task(
                self.response_channel.send(
                    f"There has been a majority vote to skip this track. "
                    f"We required at least {critical_ratio} vote(s) "
                    f"to trigger this. \nMoving to the next track...",
                    delete_after=30,
                )
            )

            # Must be called in a coroutine.
            if self.voice_client and self.voice_client.is_playing():
                self.voice_client.stop()
        else:
            self.loop.create_task(
                self.response_channel.send(
                    f"{critical_ratio - members_vote} more votes needed to skip this track."
                )
            )

    async def set_volume(self, value=100):
        if 0 <= value <= 200:
            self._player.volume = value / 100
        else:
            raise MusicSessionError(self, "Please pick a volume between 0 and 200")

    async def _player_loop(self) -> None:
        """A coroutine to run as a task to implement the player."""
        while True:
            try:
                # Wait for request
                with async_timeout.timeout(IDLE_TIMEOUT):
                    curr_request = await self.queue.get()

                    # If we have a mix at the front, then we should pop the item from that
                    # mix back onto the front of the queue. We can then reiterate to process that.

                    # If we find the mix is empty, it is dead, so just continue and it will
                    # be disposed of.
                    if isinstance(curr_request, request.Mix):
                        if len(curr_request):
                            mix = curr_request
                            curr_request = curr_request.shift()
                            await self.queue.unshift(mix)
                            await self.queue.unshift(curr_request)
                        else:
                            mix = curr_request
                            if len(self.queue):
                                # Move to the back
                                await self.queue.put(mix)
                        continue

                # We do this to spin the CPU up. On sluggish machines such as the RPi,
                # it prevents the system from distorting and screwing up the first few
                # seconds.
                for _ in range(500):
                    await asyncio.sleep(0)

                try:
                    async with self.response_channel.typing():
                        self.now_playing = curr_request

                        ffmpeg = discord.FFmpegPCMAudio(curr_request.url)

                        await self._ensure_connected()

                        self._player = discord.PCMVolumeTransformer(
                            ffmpeg, self._volume / 100
                        )

                        self.skip_votes.clear()

                        self.voice_client.play(self._player)

                        # Play the current track. On completion, attempt to
                        # set the next track event bit to continue this coroutine.
                        self.logger.info(f"Now playing {curr_request!r} in {self}")

                    async def banner(sesh):
                        def generator():
                            while True:
                                banner_pages = [
                                    curr_request.make_embeds("Now playing")[0]
                                ]

                                up_next_track = sesh.queue[0] if sesh.queue else None
                                if isinstance(up_next_track, request.Mix):
                                    up_next_track = (
                                        up_next_track[0] if len(up_next_track) else None
                                    )

                                if up_next_track:
                                    if isinstance(sesh.queue[0], request.Mix):
                                        then_track = (
                                            sesh.queue[0][1]
                                            if len(sesh.queue[0]) > 1
                                            else None
                                        )
                                    else:
                                        then_track = (
                                            sesh.queue[1]
                                            if len(sesh.queue) > 1
                                            else None
                                        )
                                else:
                                    then_track = None

                                if isinstance(then_track, request.Mix):
                                    then_track = (
                                        then_track[0] if len(then_track) else None
                                    )

                                if up_next_track:
                                    up_next = up_next_track.make_embeds("Up next...")[0]
                                else:
                                    up_next = copy.deepcopy(DEFAULT_EMBED)
                                    up_next.set_author(name="Up next...")

                                banner_pages.append(up_next)

                                if then_track:
                                    then = then_track.make_embeds("...and then...")[0]
                                else:
                                    then = copy.deepcopy(DEFAULT_EMBED)
                                    then.set_author(name="...and then...")

                                banner_pages.append(then)

                                yield from banner_pages

                        base = None

                        try:
                            state = generator()
                            base = await sesh.response_channel.send(embed=next(state))
                            await asyncio.sleep(BANNER_TIMEOUT)
                            for page in state:
                                try:
                                    base = await sesh.response_channel.get_message(
                                        base.id
                                    )
                                    if base.channel != self.response_channel:
                                        try:
                                            await base.delete()
                                        except:
                                            pass

                                        raise _WrongChannel

                                    await base.edit(embed=page)
                                except (discord.NotFound, _WrongChannel):
                                    base = await sesh.response_channel.send(embed=page)
                                finally:
                                    await asyncio.sleep(BANNER_TIMEOUT)

                        except (asyncio.TimeoutError, asyncio.CancelledError):
                            return
                        except Exception:
                            traceback.print_exc()
                        finally:
                            try:
                                if base:
                                    await base.delete()
                            except:
                                pass
                            finally:
                                sesh.banner_task = None

                    self.banner_task = self.loop.create_task(banner(self))
                except asyncio.CancelledError as ex:
                    raise ex from None
                except Exception as ex:
                    traceback.print_exc()
                    ex = MusicSessionError.maybe_wrap(self, ex)
                    await self.response_channel.send(
                        f"There was an issue playing {curr_request}; {ex}"
                    )
                    # Give up
                    break
                else:
                    # Events don't work across threads properly, so a "busy" loop is
                    # all we can really do.
                    while self.voice_client and self.is_playing:
                        await asyncio.sleep(BUSY_WAIT_POLLING_PERIOD)

            except asyncio.CancelledError:
                # Triggered if we cancel the coroutine.
                self.logger.warning(f"Cancelled player {self}.")
                break
            except asyncio.TimeoutError:
                # Debug. Todo: remove.
                traceback.print_exc()
                await self.response_channel.send("You were idle for too long...")
                self.logger.info(f"{self} was idle too long, and is disconnecting.")
                break
            except Exception:
                traceback.print_exc()
            else:
                continue
            finally:
                if self.banner_task is not None:
                    # noinspection PyUnresolvedReferences
                    self.banner_task.cancel()
                    self.banner_task = None

        # If we didn't continue, die.
        if self.voice_client.is_playing():
            await self.voice_client.stop()
        if self.voice_client.is_connected():
            await self.disconnect()
