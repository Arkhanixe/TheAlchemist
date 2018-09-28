import discord
import traceback
import sqlite3

from discord.ext import commands

conn = sqlite3.connect("database.db")
c = conn.cursor()

class Admin:
    """Admin-only commands that make the bot dynamic."""

    def owner(ctx):
        if ctx.author.id == 462351034384252938:
            return True
        else:
            return False

    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        self.sessions = set()

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    async def __local_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    def get_syntax_error(self, e):
        if e.text is None:
            return f'```py\n{e.__class__.__name__}: {e}\n```'
        return f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'

    @commands.check(owner)
    @commands.command(hidden=True)
    async def load(self, ctx, *, module):
        """Loads a module."""
        try:
            self.bot.load_extension(module)
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.check(owner)
    @commands.command(hidden=True)
    async def unload(self, ctx, *, module):
        """Unloads a module."""
        try:
            self.bot.unload_extension(module)
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.check(owner)
    @commands.command(name='reload', hidden=True)
    async def _reload(self, ctx, *, module):
        """Reloads a module."""
        try:
            self.bot.unload_extension(module)
            self.bot.load_extension(module)
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.check(owner)
    @commands.command()
    async def dm(self,ctx, id: discord.User, message):
        embed = discord.Embed(title="Message",description=f"Dear User. You have a message. Here it is: \n {message}")
        await id.send(embed=embed)

    @commands.check(owner)
    @commands.command(aliases=["ut"])
    async def uptime(self,ctx):
        delta_uptime = datetime.utcnow() - bot.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        weeks, days = divmod(days, 7)
        embed = discord.Embed(color=0x0000FF)
        embed.add_field(name="Alchemist Uptime", value=f"Weeks: **{weeks}**\nDays: **{days}**\nHours: **{hours}**\nMinutes: **{minutes}**\nSeconds: **{seconds}**")
        await ctx.send(embed=embed)

    @commands.check(owner)
    @commands.command()
    async def remmes(ctx, number: int = None):
        
        deleted = await ctx.channel.purge(
            limit = number + 1
        )

        await ctx.send(
        "Force Removed {} message(s)".format(
            len(
                deleted
            )
            ),delete_after=15
        )

    @commands.is_owner()
    @commands.command()
    async def restart(self,ctx):
        with open("Token.txt") as fp:
            token = fp.read().strip()
            bot.run(token)

def setup(bot):
    bot.add_cog(Admin(bot))