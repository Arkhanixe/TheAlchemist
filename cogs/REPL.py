
import discord
import asyncio
import json
import os
import platform
import random
import contextlib
import time
import datetime
import math
import traceback
import inspect
import textwrap
import io
import re
from discord import opus
from datetime import datetime
from discord.ext import commands
from contextlib import redirect_stdout
from some_paginator import Paginator
import sqlite3

class test:
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        self.sessions = set()

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ``````
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])
        return content

    def get_syntax_error(self, e):
        if e.text is None:
            return '```{0.__class__.__name__}: {0}\n```'.format(e)
        return '```{0.text}{1:>{0.offset}}\n{2}: {0}```'.format(e, '^', type(e).__name__)


    # -*-*- Source for exec command  -*-*-
    @commands.command(name="exec", aliases=["shell"], hidden=True)
    async def execute(self, ctx, *, code):
        """Executes the given code."""

        # Removes code blocks if they are present. This then captures the
        # syntax highlighting to use if it is present.
        code_block = re.findall(r"′′′([a-zA-Z0-9]*)\s([\s\S(^\\′{3})]*?)\s*′′′", code)

        if code_block:
            lang, code = code_block[0][0], code_block[0][1]

            if lang in ("py", "python", "python3", "python3.6", "python3.7"):
                lang = "python"
        else:
            if ctx.invoked_with == "exec":
                lang = "python"
            elif self.shell is None:
                return await ctx.send(
                    "This feature has been disabled by the bot owner.", delete_after=15
                )
            else:
                lang = self.shell

        executor = execute_in_session if lang == "python" else execute_in_shell

        additional_messages = []

        async with ctx.typing():
            # Allows us to capture any messages the exec sends, and we can delete
            # them with the paginator later.
            hooked_ctx = copy.copy(ctx)

            async def send(*args, **kwargs):
                m = await ctx.send(*args, **kwargs)
                additional_messages.append(m)
                return m

            hooked_ctx.send = send

            sout, serr, result, exec_time, prog = await executor(hooked_ctx, lang, code)

        pag = factory.StringNavigatorFactory(
            prefix="′′′diff\n",
            suffix="′′′",
            max_lines=25,
            enable_truncation=False,
            substitutions=[scrub],
        )

        nl = "\n"
        pag.add_line(f'---- {prog.replace(nl, " ")} ----')

        if sout:
            pag.add_line("- stdout:")
            for line in sout.split("\n"):
                pag.add_line(line)
        if serr:
            pag.add_line("- stderr:")
            for line in serr.split("\n"):
                pag.add_line(line)
        if len(str(result)) > 100:
            pag.add_line(f"+ Took approx {1000 * exec_time:,.2f}ms; returned:")
            for p in pprint.pformat(result, indent=4).split("\n"):
                pag.add_line(p)
        else:
            pag.add_line(f"+ Returned ′{result}′ in approx {1000 * exec_time:,.2f}ms. ")

        nav = pag.build(ctx)
        nav.start()
        await nav.is_ready.wait()
        commands.reinvoke_on_edit(ctx, *nav.all_messages, *additional_messages)

"""
            pag = commands.Paginator()
            out = Arb.split('\n')
            for i in out:
                try:
                    pag.add_line(line=i)
                except RuntimeError:
                    pag.close_page()
                    pag.add_line(line=i)
            for i in pag.pages:
                embed = discord.Embed(description=i)
                await ctx.send(embed=embed)
"""

def setup(bot):
    bot.add_cog(test(bot))

