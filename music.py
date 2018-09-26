import asyncio
import logging
import math
import os
import re
import traceback
import weakref
from datetime import timedelta
from typing import Dict

import async_timeout
import discord
import libneko
import youtube_dl

from neko2.shared import commands, traits
from . import guildsession
from . import request


class NotInVoiceChat(commands.CheckFailure):
    pass


# References:
#    https://github.com/rg3/youtube-dl#format-selection-examples
#
# My own experimentation on the Raspberry Pi 3B:
#
# CODEC | =>     | <=     | Notes
# ======x========x========x=================
# 3gp   | 150k   | 100k   | Sounds awful
# aac   | 160k   | 150k   | Pretty decent
# flv   | 150k   | 109k   | Breaks up a bit
# m4a   | 150k   | 140k   | Crisp
# mp3   | 150k   | 150k   | Choppy to start
# mp4   | 160k   | 2070k  | Choppy as hell
# ogg   | 140k   | 119k   | Smooooooooooooth  - Seems like the best option.
# wav   | 150k   | 130k   | Clear
# webm  | 140k   | 946k   | Clear             - What we generally use
YT_DL_OPTS = {
    # "format": "webm[abr>0]/bestaudio/best",
    "format": "ogg[abr>0]/m4a[abr>0]/webm[abr>0]/bestaudio/best",
    "ignoreerrors": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",
    "cachedir": False,
    "quiet": True,
    "logger": logging.getLogger("YoutubeDL"),
}

# Max clients to run at once. Set to prevent tanking the host if it is slow or
# low powered (e.g. a Raspberry Pi), or if the net connection is crap. If None,
# then the restriction is ignored, mostly.
MAX_CHANNEL_LIMIT = 3
# Time to wait before leaving an empty VC.
IDLE_TIME = 5 * 60
AT_FRONT_TOKEN = " --front "
PLAYLIST_CHUNK_INCREMENT = (os.cpu_count() - 1) or 1
MAX_PLAYLIST_SIZE = min(16 * PLAYLIST_CHUNK_INCREMENT, 50)
TRACK_REGEX = r"^(?:https?://)?((?:www|m)\.)?((?:youtube\.com|youtu\.be))(/(?:[\w\-]+\?v=|embed/|v/)?)([\w\-]+)(\S+)?$"
MIX_REGEX = r"^(?:https?://)?((?:www|m)\.)?((?:youtube\.com|youtu.be))/(?:\w+\?v=|)([\w\-]+).*[&?]list=([\w\-]+).*$"


def _get_metadata(query):
    logging.basicConfig(level="INFO")
    logging.info("_get_metadata(%s)", query)

    # Reconstruct URL from ID. This prevents urls with other
    # data in them from causing errors.
    video_id = re.match(TRACK_REGEX, query)
    if video_id:
        video_id = video_id.group(4)
        query = f"https://youtube.com/watch?v={video_id}"

    logging.info(f"Fetching metadata for %s", query)

    downloader = youtube_dl.YoutubeDL(YT_DL_OPTS)

    print(YT_DL_OPTS, query)

    info = downloader.extract_info(query, download=False)
    logging.info(f"Fetched metadata for %s", query)

    # Search invocations yield a playlist. Get the first video.
    # Raises type error if no results...
    if info and info.get("_type") == "playlist":
        entry = info["entries"][0]
    else:
        entry = info

    if entry:
        logging.info("Got the 1 expected result just fine.")
    else:
        logging.info("Got no results...")
    return entry


def _get_tracks(url, start, end, verbose=False):
    logging.basicConfig(level="INFO")
    logging.info("_get_tracks(%s, %s, %s, %s)", url, start, end, verbose)

    # noinspection PyDictCreation
    opts = {**YT_DL_OPTS, "playlist_items": ",".join(map(str, range(start, end)))}
    opts["quiet"] = not verbose
    downloader = youtube_dl.YoutubeDL(opts)
    info = downloader.extract_info(url, download=False, ie_key="YoutubePlaylist")

    logging.info(f'Got {len(info["entries"])} results.')
    return info["entries"]


# noinspection PyMethodMayBeStatic,PyBroadException
class MusicCog(traits.CogTraits):
    __NO_HOTSWAP__ = True

    def __init__(self):
        # Makes my life easier.
        self.logger.setLevel("DEBUG")
        logging.getLogger("YoutubeDL").setLevel("INFO")
        self.sessions: Dict[discord.Guild, guildsession.Session] = {}

    async def __local_check(self, ctx):
        """Only work in guilds."""
        if self.sessions.get(ctx.guild) is None:
            return True
        elif ctx.author.id == ctx.bot.owner_id:
            return True
        elif ctx.author.voice is None:
            raise NotInVoiceChat("Please enter my voice chat channel first.")
        elif ctx.author.voice.channel == self.sessions.get(ctx.guild).voice_channel:
            return True
        else:
            return False

    def __unload(self):
        for session in self.sessions.copy().values():
            asyncio.ensure_future(session.disconnect())
            asyncio.ensure_future(
                session.response_channel.send(
                    "The bot is restarting, so I will disconnect now. Sorry!"
                )
            )

    def try_delete(self, ctx):
        async def deleter():
            await asyncio.sleep(10)
            await commands.try_delete(ctx)

        ctx.bot.loop.create_task(deleter())

    async def on_voice_state_update(self, _, before, after):
        """
        Checks if the VC we are in has become empty. When it has, we leave.
        """
        # If the member just left a voice channel, check if we were also in it.
        # If we were, and the channel is now empty, we should leave it too.

        if after.channel is None and before.channel is not None:
            c = before.channel

            try:
                session = self.sessions[c.guild]

                if session.voice_channel == c:
                    if len(session.voice_channel.members) <= 1:
                        await asyncio.sleep(IDLE_TIME)

                        if len(session.voice_channel.members) <= 1:
                            await session.disconnect()
                        del session
            except KeyError:
                # We can just ignore.
                pass

    @commands.command(brief="Join the voice channel you are in.")
    async def join(self, ctx):
        try:
            if ctx.guild in self.sessions:
                raise guildsession.MusicSessionError(
                    None, "A session already exists in this server!"
                )

            if MAX_CHANNEL_LIMIT is not None and len(self.sessions) > MAX_CHANNEL_LIMIT:
                raise guildsession.MusicSessionError(
                    None, "My system is currently overloaded. Sorry :("
                )

            if not ctx.author.voice:
                raise guildsession.MusicSessionError(
                    None, "Join a voice channel first."
                )

            # Proxy to ourselves. Stops circular references.
            my_weak_proxy = weakref.proxy(self)

            session = await guildsession.Session.new(
                ctx.bot.loop,
                ctx.channel,
                ctx.author.voice.channel,
                lambda *_: my_weak_proxy.sessions.pop(ctx.guild),
            )

            self.sessions[ctx.guild] = session

            encoder = session.voice_client.encoder
            await session.response_channel.send(
                f"Connected to {session.voice_client.endpoint} at "
                f"{session.voice_client.endpoint_ip} "
                f"using {encoder.CHANNELS:,} audio channels at "
                f"{encoder.SAMPLING_RATE/1000:,.2f}kHz. "
                f"Target bitrate is {session.voice_channel.bitrate/1000:,.2f}kHz."
            )

            commands.acknowledge(ctx, timeout=5)
            return True
        except guildsession.MusicSessionError as ex:
            traceback.print_exc()
            await ctx.send(str(ex))
        return False

    def _make_request(self, title, source, info, author):
        self.logger.debug(
            "_make_request (%s, %s, %s, %s)", title, source, str(info)[:15], author
        )
        return request.Request(
            title=title,
            referral=source,
            id=info["id"],
            user=author,
            url=info["url"],
            thumbnail=info["thumbnail"],
            author=info["uploader"],
            author_url=info["uploader_url"],
            length=timedelta(seconds=math.ceil(float(info["duration"]))),
        )

    @classmethod
    async def _get_playlist(cls, url):
        cls.logger.debug("_get_playlist(%s)", url)

        # Problem with youtube_dl and playlists is that it is rather...slow. The user will probably
        # get bored of waiting two minutes for the data to be collected, you know?

        # Quick and simple way around this is to essentially play the first video, and
        # simultaneously download the rest. Kind of a crap way to do this, but eh.

        first = await cls.run_in_pp_executor(_get_metadata, [url])
        yield first

        start = 1

        futures = []

        while start <= MAX_PLAYLIST_SIZE:
            end = start + PLAYLIST_CHUNK_INCREMENT
            futures.append(cls.run_in_pp_executor(_get_tracks, [url, start, end]))
            start = end + 1

        track_list_tuple = await asyncio.gather(*futures)

        for track_list in track_list_tuple:
            for track in track_list:
                yield track

    @commands.group(
        brief="Play the given URL, or search for the query on Youtube.",
        invoke_without_command=True,
        aliases=["p"],
    )
    async def play(self, ctx, *, source):
        """
        If a URL to a video is provided, play that video's audio, otherwise,
        search YouTube for the first match for the input and play that.

        Pass the --front flag to push to the front of the queue rather than the
        rear.
        """
        at_front = False
        # Hacks to make string matching easier.
        if AT_FRONT_TOKEN in f" {source} ":
            at_front = True
            source = source.replace(AT_FRONT_TOKEN.strip(), "")

        try:
            self.logger.debug("IN PLAY")

            if ctx.guild not in self.sessions:
                r = await self.join.callback(self, ctx)

                # Returns false on error.
                if not r:
                    return

            with ctx.typing():
                try:
                    with async_timeout.timeout(15):
                        i = await self.run_in_pp_executor(_get_metadata, [source])
                except asyncio.TimeoutError:
                    traceback.print_exc()
                    i = None

                if not i:
                    raise TypeError

                title = i.get("title", source)
                session = self.sessions[ctx.guild]

            req = self._make_request(title, source, i, ctx.author)

            if at_front:
                await session.queue.unshift(req)
            else:
                await session.queue.put(req)

            nb = " "
            # Prevent @everyone exploits.
            await ctx.send(f"**@{ctx.author}:** Added {title.replace('@', '@' + nb)}.")
        except (TypeError, ValueError, AttributeError):
            traceback.print_exc()
            return await ctx.send("No results, or video is not available....")
        except guildsession.MusicSessionError as ex:
            traceback.print_exc()
            await ctx.send(f"Couldn't add the track because {ex}")
        except Exception as ex:
            traceback.print_exc()
            return await ctx.send(f"Couldn't add that because {str(ex) or repr(ex)}")

    @play.command(name="mix", brief="Adds a mix to the current queue.")
    async def play_mix(self, ctx, *, url):
        """
        Attempts to get a playlist. This will decay into a bunch of tracks as they are
        iterated across.

        Note that excessively long playlists will be truncated down to around 300 tracks.
        """
        return await self._mix(ctx, source=url)

    @commands.command(name="mix", brief="Adds a mix to the current queue.")
    async def mix(self, ctx, *, source):
        """
        Attempts to get a playlist. This will decay into a bunch of tracks as they are
        iterated across.

        Note that excessively long playlists will be truncated down to around 300 tracks.

        You can use the --front flag like with the `play` command, but it will only
        put the first track to the front. This is done to prevent obnoxious people pushing
        50-track mixes to the front of the queue.
        """
        return await self._mix(ctx, source=source)

    async def _mix(self, ctx, *, source):
        at_front = False
        # Hacks to make string matching easier.
        if AT_FRONT_TOKEN in f" {source} ":
            at_front = True
            source = source.replace(AT_FRONT_TOKEN.strip(), "")

        try:
            self.logger.debug("IN MIX")

            if ctx.guild not in self.sessions:
                r = await self.join.callback(self, ctx)

                # Returns false on error.
                if not r:
                    return

            session = self.sessions[ctx.guild]

            match = re.match(MIX_REGEX, source)
            if match:
                source = f"https://youtube.com/watch?v={match.group(3)}&list={match.group(4)}"
            else:
                raise guildsession.MusicSessionError(
                    session, "could not resolve this link"
                )

            with ctx.typing():
                total_tracks = 0

                genexp = self._get_playlist(source)

                try:
                    first = await genexp.asend(None)
                except StopAsyncIteration:
                    raise guildsession.MusicSessionError(
                        session, "could not resolve this link"
                    )

                title = first.get("title", source)
                first_request = self._make_request(
                    title, first["url"], first, ctx.author
                )

                total_tracks += 1

                # Resolve into a Mix
                mix = request.Mix(
                    source,
                    ctx.author,
                    libneko.aggregates.MutableOrderedSet[request.Request](),
                )

                has_added = False

                async def put():
                    nonlocal has_added
                    if not has_added:
                        await session.queue.put(mix)
                        has_added = True

                if not session.now_playing:
                    m = await ctx.send(
                        "I am going to play the first track while I download the rest..."
                        " Please be patient!"
                    )

                    if at_front:
                        await session.queue.unshift(first_request)
                    else:
                        await session.queue.put(first_request)

                    await put()

                else:
                    m = await ctx.send("Downloading your mix's metadata. Be patient...")
                    mix.tracks.add(first_request)

                async for item in genexp:
                    is_first = item["id"] == first_request.id
                    is_dupe = item["id"] in map(lambda t: t.id, mix.tracks)

                    if is_first or is_dupe:
                        self.logger.info(
                            f'Skipping duplicate track {item["title"]} -- {item["url"]}'
                        )
                        continue

                    await put()

                    mix.tracks.add(
                        self._make_request(
                            item["title"], item.get("alt_title"), item, ctx.author
                        )
                    )

                    self.logger.info(
                        f'Emplacing track {item["title"]} -- {item["url"]}'
                    )

                    total_tracks += 1

                await put()

            try:
                await ctx.send(
                    content=f'Added a total of {len(mix)} track{"s" if len(mix) - 1 else ""} to '
                    "the queue."
                )
                await m.delete()
            except:
                traceback.print_exc()
                pass

        except (TypeError, ValueError, AttributeError):
            traceback.print_exc()
            return await ctx.send("No results, or video is not available....")

        except guildsession.MusicSessionError as ex:
            traceback.print_exc()
            await ctx.send(f"Couldn't add the track because {ex}")

        except Exception as ex:
            traceback.print_exc()
            return await ctx.send(f"Couldn't add that because {str(ex) or repr(ex)}")

    @commands.command(brief="Request the next track be played.", aliases=["next", "s"])
    async def skip(self, ctx, *args):
        """
        If no tracks are in the queue, I will wait for about ten minutes
        and then disconnect.
        
        If you requested the track, you can force the track to skip with
        `--force` on the end of the command.

        You can skip the current playlist if there is one with `--playlist`
        """
        try:
            session = self.sessions[ctx.guild]
            if "--force" in args:
                c1 = ctx.author.id == ctx.bot.owner_id
                c2 = ctx.author == session.now_playing.user

                if c1 or c2:
                    if session.voice_client and session.voice_client.is_playing():
                        await ctx.send("Okay, master.", delete_after=15)
                        session.voice_client.stop()
                    else:
                        await ctx.send("Nothing was playing...")
                else:
                    await ctx.send("You didn't request this track!")
            else:
                session.skip(ctx.author)
                if "--playlist" in args:
                    if isinstance(session.queue[0], request.Mix):
                        await session.queue.get()
        except KeyError:
            return await ctx.send(
                "Join a voice channel first and run the `join` command. "
                "Then add some tracks with `play`"
            )
        except guildsession.MusicSessionError as ex:
            traceback.print_exc()
            await ctx.send(ex)
            return self.try_delete(ctx)
        else:
            commands.acknowledge(ctx, timeout=None)

    @commands.command(brief="Pops the last track from the queue.", aliases=["d"])
    async def pop(self, ctx):
        """This only works if you requested that track."""
        try:
            session = self.sessions[ctx.guild]

            c1 = ctx.author.id == ctx.bot.owner_id
            c2 = session.queue[-1].user == ctx.author

            if c1 or c2:
                item = await session.queue.pop()
                nb = " "
                # Prevent @everyone exploits.
                await ctx.send(
                    f"Successfully removed {str(item).replace('@', '@' + nb)} from the back of "
                    f"the queue.",
                    delete_after=10,
                )
            else:
                await ctx.send(
                    "You don't have permission to do this. Only the requester can pop.",
                    delete_after=10,
                )
                return self.try_delete(ctx)
        except KeyError:
            traceback.print_exc()
            await ctx.send("I am not playing in this server.", delete_after=10)
            return self.try_delete(ctx)
        except IndexError:
            traceback.print_exc()
            await ctx.send("The queue is empty.", delete_after=10)
            return self.try_delete(ctx)
        else:
            commands.acknowledge(ctx)

    @commands.command(brief="Move me to a different voice channel.", aliases=["move"])
    async def movevoice(self, ctx, destination: discord.VoiceChannel):
        try:
            await self.sessions[ctx.guild].move_to(destination)
        except KeyError:
            await ctx.send("I am not playing in this server.", delete_after=10)
            return self.try_delete(ctx)
        else:
            commands.acknowledge(ctx)

    @commands.command(brief="Change the channel I send VC-related messages to.")
    async def movetext(self, ctx, destination: discord.TextChannel):
        try:
            await self.sessions[ctx.guild].move_to(destination)
        except KeyError:
            await ctx.send("I am not playing in this server.", delete_after=10)
            return self.try_delete(ctx)
        else:
            commands.acknowledge(ctx)

    @commands.command(
        brief="Leave the audio channel in this server.", aliases=["bye", "stop"]
    )
    async def leave(self, ctx):
        try:
            await self.sessions[ctx.guild].disconnect()
            commands.acknowledge(ctx, timeout=5)
        except KeyError:
            await ctx.send("I am not playing in this server.", delete_after=10)
            return self.try_delete(ctx)
        except guildsession.MusicSessionError as ex:
            await ctx.send(ex, delete_after=10)
        except Exception:
            pass

        commands.acknowledge(ctx, timeout=None)

    @commands.command(brief="Display the music queue.", aliases=["q"])
    async def queue(self, ctx):
        try:
            session = self.sessions[ctx.guild]

            track_embeds = (
                [session.now_playing.make_embeds()[0]] if session.now_playing else []
            )
            for track in session.queue:
                track_embeds.extend(track.make_embeds())

            if not track_embeds:
                return await ctx.send(
                    "The queue is empty. If you have added tracks that have "
                    "yet to be played, then they may still be loading."
                )

            nav = libneko.EmbedNavigator(ctx, track_embeds)
            nav.start()

        except KeyError:
            traceback.print_exc()
            await ctx.send("I am not playing in this server.", delete_after=10)
            return self.try_delete(ctx)
        except guildsession.MusicSessionError as ex:
            traceback.print_exc()
            await ctx.send(ex)

    @commands.command(brief="Pauses the player")
    async def pause(self, ctx):
        try:
            session = self.sessions[ctx.guild]

            if not session.voice_client.is_paused():
                session.voice_client.pause()
                commands.acknowledge(ctx, emoji="\N{DOUBLE VERTICAL BAR}", timeout=None)
            else:
                commands.acknowledge(ctx, timeout=5)
        except KeyError:
            await ctx.send("I am not playing in this server.", delete_after=10)
            return self.try_delete(ctx)

    @commands.command(brief="Resumes the player.")
    async def resume(self, ctx):
        try:
            session = self.sessions[ctx.guild]

            if session.voice_client.is_paused():
                session.voice_client.resume()
                commands.acknowledge(
                    ctx, emoji="\N{BLACK RIGHT-POINTING TRIANGLE}", timeout=None
                )
            else:
                commands.acknowledge(ctx, timeout=5)
        except KeyError:
            await ctx.send("I am not playing in this server.", delete_after=10)
            return self.try_delete(ctx)

    @commands.command(brief="Replays the track next.")
    async def replay(self, ctx):
        try:
            session = self.sessions[ctx.guild]
            if not session.now_playing:
                await ctx.send("Nothing has played yet.")
            else:
                await session.queue.unshift(session.now_playing)
                commands.acknowledge(ctx, timeout=5)

        except KeyError:
            await ctx.send("I am not playing in this server.", delete_after=10)
            return self.try_delete(ctx)
        except guildsession.MusicSessionError as ex:
            await ctx.send(ex)

    async def _volume(self, ctx, value: float):
        try:
            session = self.sessions[ctx.guild]

            if not session.now_playing:
                return await ctx.send("Nothing has played yet.")

            await session.set_volume(value)
            commands.acknowledge(ctx)
        except KeyError:
            await ctx.send("I am not playing in this server.", delete_after=10)
            return self.try_delete(ctx)
        except ValueError:
            await ctx.send("Please give a number!", delete_after=10)
            return self.try_delete(ctx)

    @commands.command(brief="Changes the volume. Defaults to 100%.", aliases=["vol"])
    async def volume(self, ctx, value: str = "100%"):
        try:
            self.try_delete(ctx)

            if value.endswith("%"):
                value = value[:-1]

            value = float(value)

            await self._volume(ctx, value)
        except guildsession.MusicSessionError as ex:
            await ctx.send(ex)
            return self.try_delete(ctx)

    @commands.command(brief="Mutes the bot, but keeps playing.")
    async def mute(self, ctx):
        try:
            self.try_delete(ctx)
            await self._volume(ctx, 0)
        except guildsession.MusicSessionError as ex:
            await ctx.send(ex)
            return self.try_delete(ctx)

    @commands.command(brief="Unmutes the bot... or resets the volume to max.")
    async def unmute(self, ctx):
        try:
            self.try_delete(ctx)
            await self._volume(ctx, 100)
        except guildsession.MusicSessionError as ex:
            await ctx.send(ex)
            return self.try_delete(ctx)

    @commands.command(brief="Shows info about the current track.")
    async def this(self, ctx):
        try:
            session = self.sessions[ctx.guild]
            np = session.now_playing

            nav = libneko.EmbedNavigator(ctx, np.make_embeds())
            nav.start()

        except KeyError:
            await ctx.send("I am not playing in this server.", delete_after=10)
            return self.try_delete(ctx)
        except guildsession.MusicSessionError as ex:
            await ctx.send(ex)
