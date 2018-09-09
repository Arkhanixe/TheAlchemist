
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
from discord import opus
from datetime import datetime
from discord.ext import commands
from contextlib import redirect_stdout

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


    @commands.command(pass_context=True, hidden=True, name='exec',aliases=["eval"])
    async def _eval(self, ctx, *, body):
        if ctx.message.author.id != 462351034384252938:
            return False
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.message.channel,
            'author': ctx.message.author,
            'guild': ctx.guild,
            'message': ctx.message
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = 'async def func():\n%s' % textwrap.indent(body, '  ')

        try:
            exec(to_compile, env)
        except SyntaxError as e:
            return await ctx.send(self.get_syntax_error(e))

        func = env['func']
        try:
            with contextlib.redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send('{}{}\n'.format(value, traceback.format_exc()))
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except Exception as e:
                await ctx.send(e)

            Arb = await ctx.send('%s%s\n' % (value, ret))
            if ret is None:
                if value:
                    Arb = await ctx.send("%s\n" % value)
                else:
                    self._last_result = ret
                    Arb = await ctx.send('%s%s\n' % (value, ret))

            pag = commands.Paginator()
            out = Arb.split('\n')
            for i in out:
                try:
                    pag.add_line(line=i)
                except RuntimeError:
                    pag.close_page()
                    pag.add_line(line=i)
            for i in pag.pages:
                await ctx.send(i)

def setup(bot):
    bot.add_cog(test(bot))

