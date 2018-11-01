#stolen from libneko ofc


import discord
from discord.ext import commands as _commands

import libneko
from libneko import embeds, strings, other
from libneko.pag import navigator

from typing import Iterable

from random import choice


class Help:
    """
    Parameters:
        dm: Defines if the help message should be send thought dm or not. Default is set to False
        colour: Defines the list of colors that the help command will cycle through when making the
        command list or randomly choose from when making a specific help page.
    """

    def __init__(
        self,
        dm: bool = False,
        colors: Iterable = None,
        colours: Iterable = None,
        cmds_per_page: int = 15,
    ):
        self.dm = dm
        self.cmds_per_page = cmds_per_page

        if colours and colors:
            raise TypeError(
                "You must only provide either one of the colour parameters!"
            )
        if colors:
            colours = colors
        if colours:
            self.hex_values = []
            for c in colours:
                try:
                    if c.startswith("#"):
                        c = c[1:]
                    self.hex_values.append(int(c, 16))
                except ValueError:
                    continue
        else:
            self.hex_values = None

    def make_help_page(self, cmd, prefix):
        """
        Makes a help page for the given command with the given prefix.
        """
        '''
        if self.hex_values:
            colour = choice(self.hex_values)
        else:
            colour = other.random_colour()
        '''



        '''










        uncomment shit above if the bot doesnt work











        '''
        title = f"`{cmd.qualified_name}` help page"
        if isinstance(cmd, _commands.Group):
            title = f"**[GROUP]** `{cmd.qualified_name}` help page"
        em = embeds.Embed(
            title=title, description=cmd.brief, colour=0x36393f, timestamp=None
        )
        em.add_field(name="Usage", value=f"```md\n{prefix}{cmd.signature}```")
        em.add_field(
            name="Full Description", value=f"{cmd.help or '`No description set yet`'}"
        )
        em.add_field(name="Category", value=f"`{cmd.cog_name}`" or "`Unsorted`")
        if isinstance(cmd, _commands.Group):
            childcmds_short_info = {
                f"\N{BULLET} `{c.name}` - {c.brief}"
                for c in sorted(cmd.commands, key=str)
                if isinstance(c, _commands.Command)
            }
            childgroups_short_info = {
                f"\N{BULLET} `{c.name}` - {c.brief}"
                for c in sorted(cmd.commands, key=str)
                if isinstance(c, _commands.Group)
            }
            if childgroups_short_info:
                em.add_field(
                    name="Subgroups",
                    value=strings.pretty_list(childgroups_short_info, sep="\n"),
                )
            em.add_field(
                name="Subcommands",
                value=strings.pretty_list(childcmds_short_info, sep="\n"),
            )
        return em

    def make_help_pages(
        self, ctx, cmds: list, pages: list, cog: str = None, step: int = 10
    ):
        """
        Makes pages (sorted by cogs) for the command iterable given.
        """

        cursor = 0

        title = "**Unsorted** Category"
        if cog:
            title = f"**{cog}** Category"
        
        for i in range(0, len(cmds), step):
            '''if self.hex_values:
                if cursor <= len(self.hex_values) - 1:
                    color = self.hex_values[cursor]
                else:
                    cursor = 0
            else:
                colour = other.random_colour()'''
            
            page = embeds.Embed(title=title, colour=0x36393f, timestamp=None)
            quest = "\N{BLACK QUESTION MARK ORNAMENT}"
            page.set_author(
                name=f"{quest} {ctx.bot.user.name}'s Commands {quest}",
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

                brief = cmd.brief or "`No brief set yet`"

                page.add_field(
                    name=name, value=f"\N{EM SPACE}{brief}" or "\N{EM SPACE}"
                )
            pages.append(page)

            cursor += 1

    @libneko.command(aliases=["h"], brief="Shows this page")
    async def help(self, ctx, *, query: str = None):
        """
        Shows a brief paginated list of all commands available in this bot.
        You can also specify a command to see more indepth details about it.
        """

        channel = ctx.channel
        if self.dm:
            if ctx.guild is not None:
                await ctx.send(
                    embed=embeds.Embed(
                        description="Commands have been sent to your DM", timestamp=None
                    )
                )
                channel = ctx.author

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
                        ctx,
                        sorted(filtered_cog_cmds, key=str),
                        pages,
                        cog=cog,
                        step=self.cmds_per_page,
                    )
                filtered_unsorted_cmds = [
                    c for c in filtered_commands if not c.cog_name
                ]
                self.make_help_pages(
                    ctx, filtered_unsorted_cmds, pages, step=self.cmds_per_page
                )
            else:
                self.make_help_pages(
                    ctx, filtered_commands, pages, step=self.cmds_per_page
                )
            nav = navigator.EmbedNavigator(pages=pages, ctx=ctx)
            nav.channel = channel
            nav.start()

        else:
            searched_command = ctx.bot.get_command(query)
            if searched_command is None or (
                searched_command.root_parent is not None
                and searched_command.root_parent not in filtered_commands
            ):
                return await ctx.send(
                    embed=embeds.Embed(
                        description=":octagonal_sign: That isn't a valid command!",
                        colour=discord.Colour.red(),
                        timestamp=None,
                    )
                )

            nav = navigator.EmbedNavigator(
                pages=[self.make_help_page(searched_command, ctx.prefix)], ctx=ctx
            )
            nav.channel = channel
            nav.start()


def setup(bot):
    """Add the cog to the bot directly. Enables this to be loaded as an extension."""
    bot.remove_command("help")
    bot.add_cog(Help())
