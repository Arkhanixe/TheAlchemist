#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Steals an emoji.

===

MIT License

Copyright (c) 2018 Koyagami

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import re

from libneko import commands, pag, converters

from neko2.shared import theme

static_re = re.compile(r"<:([^:]+):(\d+)>")
animated_re = re.compile(r"<a:([^:]+):(\d+)>")


class GrandTheftEmojiCog:
    @staticmethod
    async def find_emojis(channel, limit):
        animated, static, message = [], [], None

        async for message in channel.history(limit=limit):
            animated.extend(animated_re.findall(message.content))
            static.extend(static_re.findall(message.content))

            if animated or static:
                break

        return animated, static, message

    @commands.command(
        brief="Steals emojis and sends to your inbox",
        aliases=["loot", "swag", "pinch", "nick"],
    )
    async def steal(self, ctx, *, message=None):
        """
        Takes a message ID for the current channel, or if not, a string message containing
        the emojis you want to steal. If you don't specify anything, I look through the
        past 200 messages. Using `^` will have the same effect, and mostly exists for legacy
        and/or muscle memory with other commands.
        
        I get all custom emojis in the message and send them to your inbox with links; this
        way, you can download them or add them to your stamp collection or whatever the hell
        you do for fun.
        
        Teach those Nitro users no more big government. Break their hearts out. FINISH THEM.
        VIVA LA REVOLUTION!
        """
        if not message or message == "^":
            animated, static, message = await self.find_emojis(ctx.channel, 200)
        else:
            try:
                message = int(message)
                message = await ctx.channel.get_message(message)
            except ValueError:
                message = ctx.message
            finally:
                animated = animated_re.findall(message.content)
                static = static_re.findall(message.content)

        if not static and not animated or not message:
            return await ctx.send("No custom emojis could be found...", delete_after=10)

        paginator = pag.Paginator(enable_truncation=False)

        paginator.add_line(f"Emoji loot from {message.jump_url}")
        paginator.add_line()

        for name, id in static:
            paginator.add_line(f" ⚝ {name}: https://cdn.discordapp.com/emojis/{id}.png")

        for name, id in animated:
            paginator.add_line(
                f" ⚝ {name}: https://cdn.discordapp.com/emojis/{id}.gif <animated>"
            )

        async with ctx.typing():
            for page in paginator.pages:
                await ctx.author.send(page)

        tot = len(animated) + len(static)
        await ctx.send(
            f'Check your DMs. You looted {tot} emoji{"s" if tot - 1 else ""}!',
            delete_after=7.5,
        )
        try:
            await ctx.message.delete()
        except:
            pass

    @staticmethod
    def transform_mute(emojis):
        return [str(emoji) + " " for emoji in emojis]

    @staticmethod
    def transform_verbose(emojis):
        return [
            f"{emoji} = {emoji.name}\n"
            for emoji in sorted(emojis, key=lambda e: e.name.lower())
        ]

    @commands.command(aliases=["emojis"])
    async def emojilibrary(self, ctx, arg=None):
        """Shows all emojis I can see ever. Pass the --verbose/-v flag to see names."""
        if arg:
            transform = self.transform_verbose
        else:
            transform = self.transform_mute

        emojis = transform(ctx.bot.emojis)

        p = pag.StringNavigatorFactory()
        for emoji in emojis:
            p += emoji

        p.start(ctx)

    @commands.command(aliases=["search"])
    async def searchemoji(self, ctx, emoji: converters.EmojiConverter):
        """Gets an emoji I can see from any guild I am in..."""
        embed = theme.generic_embed(
            ctx, title=emoji.name, description=str(emoji), url=emoji.url
        )
        embed.set_footer(text=str(emoji.guild))
        embed.set_image(url=emoji.url)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(GrandTheftEmojiCog())
