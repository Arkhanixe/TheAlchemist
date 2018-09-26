
import discord
from discord.ext import commands

import asyncio
from async_timeout import timeout
from functools import partial
from youtube_dl import YoutubeDL


ytdlopts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': False,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # ipv6 addresses cause issues sometimes
}

ffmpegopts = {
    'before_options': '-nostdin',
    'options': '-vn'
}

ytdl = YoutubeDL(ytdlopts)


class VoiceConnectionError(commands.CommandError):
    """Custom Exception class for connection errors."""


class InvalidVoiceChannel(VoiceConnectionError):
    """Exception for cases of invalid Voice Channels."""


class YTDLSource(discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester

        self.title = data.get('title')
        self.web_url = data.get('webpage_url')

        # YTDL info dicts (data) have other useful information you might want
        # https://github.com/rg3/youtube-dl/blob/master/README.md

    def __getitem__(self, item: str):
        """
        Allows us to access attributes similar to a dict.

        This is only useful when you are NOT downloading.
        """
        return self.__getattribute__(item)

    @classmethod
    async def create_source(cls, ctx, search: str, *, loop, download=False):
        loop = loop or asyncio.get_event_loop()

        to_run = partial(ytdl.extract_info, url=search, download=download)
        data = await loop.run_in_executor(None, to_run)

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        if download:
            source = ytdl.prepare_filename(data)
        else:
            return {'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title']}

        return cls(discord.FFmpegPCMAudio(source), data=data, requester=ctx.author)

    @classmethod
    async def regather_stream(cls, data, *, loop):
        """
        Used for preparing a stream, instead of downloading.

        Since Youtube Streaming links expire.
        """
        loop = loop or asyncio.get_event_loop()
        requester = data['requester']

        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)

        return cls(discord.FFmpegPCMAudio(data['url']), data=data, requester=requester)


class MusicPlayer:
    """
    A class which is assigned to each guild using the bot for Music.

    This class implements a queue and loop, which allows for different guilds to listen to different playlists
    simultaneously.

    When the bot disconnects from the Voice it's instance will be destroyed.
    """

    __slots__ = ('bot', '_guild', '_channel', '_cog', 'queue', 'next', 'current', 'np', 'volume', 'repeat', 'repeating')

    def __init__(self, ctx):
        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.np = None  # Now playing message
        self.volume = .5
        self.current = None
        self.repeat = False
        self.repeating = None

        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        """Our main player loop."""
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            try:
                # Wait for the next song. If we timeout cancel the player and disconnect...
                async with timeout(300):  # 5 minutes...
                    if self.repeat and self.current is not None:
                        source = self.repeating
                    else:
                        source = await self.queue.get()
                        self.repeating = source
            except asyncio.TimeoutError:
                return self.destroy(self._guild)

            if not isinstance(source, YTDLSource):
                # Source was probably a stream (not downloaded)
                # So we should regather to prevent stream expiration
                try:
                    source = await YTDLSource.regather_stream(source, loop=self.bot.loop)
                except Exception as e:
                    await self._channel.send(f'There was an error processing your song.\n'
                                             f'```css\n[{e}]\n```')
                    continue

            source.volume = self.volume
            self.current = source

            self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            embed=discord.Embed(
                description=f"Now Playing: {source.title}\nRequested By: {source.requester}",
                color=self.bot.cardinal.randColour()
            )
            self.np = await self._channel.send(embed=embed)
            await self.next.wait()

            # Make sure the FFmpeg process is cleaned up.
            source.cleanup()

            try:
                # We are no longer playing this song...
                await self.np.delete()
            except discord.HTTPException:
                pass

    def destroy(self, guild):
        """Disconnect and cleanup the player."""
        return self.bot.loop.create_task(self._cog.cleanup(guild))


class music:
    """Music related commands."""

    __slots__ = ('bot', 'cas', 'players')

    def __init__(self, bot):
        self.bot = bot
        self.cas = bot.cardinal
        self.players = {}

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    async def __local_check(self, ctx):
        """A local check which applies to all commands in this cog."""
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    async def __error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send(embed=discord.Embed(description='This command can not be used in Private Messages.', color=self.bot.cardinal.randColour()))
            except discord.HTTPException:
                pass
        elif isinstance(error, InvalidVoiceChannel):
            await ctx.send('Error connecting to Voice Channel. '
                           'Please make sure you are in a valid channel or provide me with one')

    def get_player(self, ctx):
        """Retrieve the guild player, or generate one."""
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player

    @commands.command(brief="Summons the player.")
    async def summon(self, ctx):
        """Connects to the users voice channel!"""
        try:
            channel = ctx.author.voice.channel
        except AttributeError:
            raise InvalidVoiceChannel('You are not currently in a voice channel!')

        vc = ctx.voice_client

        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Moving to channel: <{channel}> timed out.')
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Connecting to channel: <{channel}> timed out.')

        await ctx.send(embed=discord.Embed(description=f'Connected to: {channel}', color=self.bot.cardinal.randColour()), delete_after=20)

    @commands.command(brief="Plays/Queues a new song!")
    async def play(self, ctx, *, search: str):
        """
        Starts the player if it isn't running! If music is already playing,
        it will add new songs to the queue!

        Usage: (pre)play [search term or youtube url]
        """
        if len(ctx.message.embeds) > 0:
            return

        async with ctx.typing():
            def vc(ctx):
                return ctx.voice_client

            if not vc(ctx):
                await ctx.invoke(self.summon)
                await asyncio.sleep(5)

            if ctx.author in vc(ctx).channel.members:
                try:
                    player = self.get_player(ctx)

                    # If download is False, source will be a dict which will be used later to regather the stream.
                    # If download is True, source will be a discord.FFmpegPCMAudio with a VolumeTransformer.
                    source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop, download=False)

                    if "ear" and "rape" not in source["title"].lower():
                        embed = discord.Embed(
                            description=f"Added {source['title']} to the Queue!",
                            color=self.bot.cardinal.randColour()
                        )
                        await ctx.send(embed=embed, delete_after=15)
                        return await player.queue.put(source)
                    embed=discord.Embed(
                        description=f"""The song {source['title']} was filtered out as potential ear rape!""",
                        color=self.bot.cardinal.randColour()
                    )
                    await ctx.send(embed=embed, delete_after=15)
                except Exception as e:
                    embed=discord.Embed(
                        description="I was not able to find that video!",
                        color=self.bot.cardinal.randColour()
                    )
                    await ctx.send(embed=embed)

    @commands.command(brief="Pauses the current song.")
    async def pause(self, ctx):
        """Pause the currently playing song."""
        vc = ctx.voice_client

        if vc is not None and ctx.author in vc.channel.members:
            if not vc or not vc.is_playing():
                return await ctx.send(embed=discord.Embed(description='I am not currently playing anything!', color=self.bot.cardinal.randColour()), delete_after=20)
            elif vc.is_paused():
                return

            vc.pause()
            await ctx.send(embed=discord.Embed(description=f'{ctx.author}: Paused the song!', color=self.bot.cardinal.randColour()))

    @commands.command(brief="Resumes the current song.")
    async def resume(self, ctx):
        """Resume the currently paused song."""
        vc = ctx.voice_client

        if vc is not None and ctx.author in vc.channel.members:
            if not vc or not vc.is_connected():
                return await ctx.send(embed=discord.Embed(description='I am not currently playing anything!', color=self.bot.cardinal.randColour()), delete_after=20)
            elif not vc.is_paused():
                return

        vc.resume()
        await ctx.send(embed=discord.Embed(description=f'{ctx.author}: Resumed the song!', color=self.bot.cardinal.randColour()))

    @commands.command(aliases=["fs"], brief="Forceskips the song!")
    @commands.has_permissions(manage_guild=True)
    async def forceskip(self, ctx):
        """
        Force skips the song!

        Requires "manage_guild" perms!
        """
        vc = ctx.voice_client
        if vc is not None and ctx.author in vc.channel.members:
            if not vc or not vc.is_connected():
                embed = discord.Embed(
                    title="Music Player",
                    description="I am not currently playing anything!",
                    color=self.bot.cardinal.randColour()
                )
                return await ctx.send(embed=embed, delete_after=20)
            if vc.is_paused():
                pass
            elif not vc.is_playing():
                return

        vc.stop()

    @commands.command(brief="Skips the song.")
    async def skip(self, ctx):
        """Skip the currently playing song."""
        vc = ctx.voice_client
        if vc is not None and ctx.author in vc.channel.members:
            if not vc or not vc.is_connected():
                embed = discord.Embed(
                    title="Music Player",
                    description="I am not currently playing anything!",
                    color=self.bot.cardinal.randColour()
                )
                return await ctx.send(embed=embed, delete_after=20)
            if vc.is_paused():
                pass
            elif not vc.is_playing():
                return

            def stop():
                vc.stop()

            if len(vc.channel.members) > 2:
                embed = discord.Embed(
                    title="Music Player",
                    description=f"""
{ctx.author.mention} has requested the current song be skipped!
If a majority vote is reached, I will skip this track!""",
                    color=self.bot.cardinal.randColour()
                )
                msg = await ctx.send(embed=embed)
                await msg.add_reaction("✅")
                await asyncio.sleep(1)
                await msg.add_reaction("❎")
                await asyncio.sleep(1)
                pro = 0
                against = 0
                total = len(vc.channel.members) - 1

                def check(r, u):
                    return u in vc.channel.members

                try:
                    for i in range(120):
                        reaction, user = await self.bot.wait_for("reaction_add", check=check)
                        if pro >= total * .75:
                            stop()
                            break
                        elif against >= total * .75:
                            raise Exception
                        elif str(reaction.emoji) == "✅":
                            pro = pro + 1
                        elif str(reaction.emoji) == "❎":
                            against = against + 1
                        await asyncio.sleep(1)
                    emebd = discord.Embed(
                        title="Music Player",
                        description="A majority was reached! Skipping...",
                        color=self.bot.cardinal.randColour()
                    )
                except Exception as e:
                    embed = discord.Embed(
                        description="A majority vote was not reached!",
                        color=self.bot.cardinal.randColour()
                    )
                await msg.edit(embed=embed, delete_after=20)
            else:
                embed = discord.Embed(
                    description="The song has been skipped!",
                    color=self.bot.cardinal.randColour()
                )
                await ctx.send(embed=embed, delete_after=20)
                stop()

    @commands.command(aliases=['q'], brief="Provides queued songs")
    async def queue(self, ctx):
        """Provides a list of upcoming songs!"""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send(embed=discord.Embed(description='I am not currently connected to voice!', color=self.bot.cardinal.randColour()), delete_after=20)

        player = self.get_player(ctx)
        if player.queue.empty():
            return await ctx.send(embed=discord.Embed(description='There are currently no more queued songs.', color=self.bot.cardinal.randColour()))

        text = "\n\n".join(i["title"] for i in player.queue._queue)

        await self.cas.Pager().embed_generator_send(self.bot, ctx, text,  lines=20, title=f'In Queue - {len(player.queue._queue)}')

    @commands.command(aliases=['np'], brief="Displays the current song")
    async def playing(self, ctx):
        """Display information about the currently playing song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send(embed=discord.Embed(description='I am not currently connected to voice!', color=self.bot.cardinal.randColour()), delete_after=20)

        player = self.get_player(ctx)
        if not player.current:
            return await ctx.send(embed=discord.Embed(description='I am not currently playing anything!', color=self.bot.cardinal.randColour()))

        try:
            # Remove our previous now_playing message.
            await player.np.delete()
        except discord.HTTPException:
            pass

        embed=discord.Embed(description=f"Now Playing: {vc.source.title}\nRequested By: {vc.source.requester}", color=self.bot.cardinal.randColour())
        player.np = await ctx.send(embed=embed)

    @commands.command(aliases=['vol'], brief="Changes the player volume!")
    async def volume(self, ctx, *, vol: float):
        """Change the player volume. Please specify a value between 1 and 100!"""
        vc = ctx.voice_client
        if vc is not None and ctx.author in vc.channel.members:
            if not vc or not vc.is_connected():
                return await ctx.send(embed=discord.Embed(description='I am not currently connected to voice!', color=self.bot.cardinal.randColour()), delete_after=20)

            if not 0 < vol < 101:
                return await ctx.send(embed=discord.Embed(description='Please enter a value between 1 and 100.', color=self.bot.cardinal.randColour()), delete_after=20)

            player = self.get_player(ctx)

            if vc.source:
                vc.source.volume = vol / 100

            player.volume = vol / 100
            await ctx.send(embed=discord.Embed(description=f'{ctx.author}: Set the volume to {vol}%', color=self.bot.cardinal.randColour()))

    @commands.command(brief="Changes the player volume!")
    async def repeat(self, ctx):
        """Repeats the currently playing song"""
        vc = ctx.voice_client
        if vc is not None and ctx.author in vc.channel.members:
            if not vc or not vc.is_connected():
                return await ctx.send(embed=discord.Embed(description='I am not currently connected to voice!', color=self.bot.cardinal.randColour()), delete_after=20)
            try:
                player = self.get_player(ctx)

                if player.repeat:
                    player.repeat = False
                    out = f"The song {vc.source.title} is no longer on repeat!"
                else:
                    player.repeat = True
                    out = f"The song {vc.source.title} is now on repeat!"

            except AttributeError:
                out = "There is not currently a song playing!"
            embed = discord.Embed(description=out, color=self.bot.cardinal.randColour())
            await ctx.send(embed=embed)

    @commands.command(aliases=["destroy"], brief="Stops and kills the player!")
    async def stop(self, ctx):
        """Stop the currently playing song and destroy the player."""
        vc = ctx.voice_client
        if vc is not None and ctx.author in vc.channel.members:
            if not vc or not vc.is_connected():
                embed = discord.Embed(
                    description='I am not currently playing anything!',
                    color=self.bot.cardinal.randColour()
                )
                return await ctx.send(embed=embed)
            await self.cleanup(ctx.guild)
            embed=discord.Embed(
                description="The player has been stopped!",
                color=self.bot.cardinal.randColour()
            )
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(music(bot))
