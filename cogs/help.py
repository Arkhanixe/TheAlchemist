#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# MIT License
#
# Copyright (c) 2018 Neko404NotFound
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in a$
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""
An extension that can be loaded 
"""

import discord
from discord.ext import commands as _commands

import libneko
from libneko import embeds, other


class Help:
    """
    Parameters:
        dm(bool): Defines if the help message should be send thought dm or not. Default is set to False

    Note:
        If the command in executed in dm, the command will act as if the dm value is set to True
    """

    def __init__(self, dm=False):
        self.dm = dm

    @staticmethod
    def make_help_page(ctx, cmd, prefix):
        """Makes a help page for the given command with the given prefix"""
        title = f"`{cmd.qualified_name}` help page"
        if isinstance(cmd, _commands.Group):
            title = f"**[GROUP]** `{cmd.qualified_name}` help page"
        em = embeds.Embed(title=title, description=cmd.brief, timestamp=None)
        em.add_field(name="Usage", value=f"```md\n{prefix}{cmd.signature}```")
        em.add_field(
            name="Full Description", value=f"{cmd.help or '`No description set yet`'}"
        )
        em.add_field(name="Category", value=f"`{cmd.cog_name}`" or "`Unsorted`")
        if isinstance(cmd, _commands.Group):
            childcmds_short_info = {
                f"• `{c.name}` - {c.brief}"
                for c in sorted(cmd.commands, key=str)
                if isinstance(c, _commands.Command)
            }
            childgroups_short_info = {
                f"• `{c.name}` - {c.brief}"
                for c in sorted(cmd.commands, key=str)
                if isinstance(c, _commands.Group)
            }
            if childgroups_short_info:
                em.add_field(
                    name="Subgroups",
                    value=other.pretty_list(childgroups_short_info, sep="\n"),
                )
            em.add_field(
                name="Subcommands",
                value=other.pretty_list(childcmds_short_info, sep="\n"),
            )
        return em

    @staticmethod
    def make_help_pages(ctx, cmds: list, pages: list, cog: str = None, step: int = 10):
        """Makes pages (sorted by cogs) for the command iterable given."""
        title = "**Unsorted** Category"
        if cog:
            title = f"**{cog}** Category"
        for i in range(0, len(cmds), step):
            page = embeds.Embed(title=title, timestamp=None)
            page.set_author(
                name=f"❓ {ctx.bot.user.name}'s Commands ❓",
                icon_url=ctx.bot.user.avatar_url,
            )
            page.set_footer(
                icon_url=ctx.bot.user.avatar_url,
                text="Only commands you can run are visible",
            )
            next_commands = cmds[i : i + 10]
            for cmd in next_commands:
                name = cmd.name
                if isinstance(cmd, _commands.Group):
                    name = "**[GROUP]** " + cmd.name
                page.add_field(
                    name=name,
                    value=f"\N{EM SPACE}{cmd.brief}"
                    or "\N{EM SPACE}`No brief set yet`",
                )
            pages.append(page)

    @libneko.command(aliases=["h"], brief="Shows this page")
    async def help(self, ctx, *, query: str = None):
        """
        Shows a brief list of all commands available in this bot.
        You can also specify a command to see more indepth details about it.
        """
        if self.dm is True:
            if ctx.guild is None:
                await ctx.send(
                    embed=embeds.Embed(
                        description="Commands have been sent to your DM", timestamp=None
                    )
                )
                ctx.guild = None
        all_commands = list(sorted(ctx.bot.commands, key=str))
        filtered_commands = []
        for cmd in all_commands:
            try:
                if await cmd.can_run(ctx) and not cmd.hidden and cmd.enabled:
                    filtered_commands.append(cmd)
            except Exception:
                continue
        if not query:
            pages = []
            if ctx.bot.cogs:
                for cog in ctx.bot.cogs:
                    filtered_cog_cmds = [
                        c
                        for c in ctx.bot.get_cog_commands(cog)
                        if c in filtered_commands
                    ]
                    self.make_help_pages(
                        ctx, sorted(filtered_cog_cmds, key=str), pages, cog
                    )
                filtered_unsorted_cmds = [
                    c for c in filtered_commands if not c.cog_name
                ]
                self.make_help_pages(ctx, filtered_unsorted_cmds, pages)
            else:
                self.make_help_pages(ctx, filtered_commands, pages)
            await other.embed_dm_or_guild(ctx, pages)
        else:
            searched_command = ctx.bot.get_command(query)
            if searched_command == None or (
                searched_command.root_parent != None
                and searched_command.root_parent not in filtered_commands
            ):
                return await ctx.send(
                    embed=embeds.Embed(
                        description="<:crossmark:465507499144118272> That isn't a valid command!",
                        colour=discord.Colour.red(),
                        timestamp=None,
                    )
                )

            await other.embed_dm_or_guild(
                ctx, [self.make_help_page(searched_command, ctx.prefix)]
            )


def setup(bot):
    """Add the cog to the bot directly. Enables this to be loaded as an extension."""
    bot.remove_command("help")
    bot.add_cog(Help())
