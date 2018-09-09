import discord
from discord.ext import commands

class Cmds:
	def __init__(self,bot):
		self.bot = bot

#	@commands.command()
#	async def invite(self,ctx):
#		await ctx.send("https://discordapp.com/api/oauth2/authorize?client_id=484204301862830090&permissions=-1&scope=bot")

def setup(bot):
    bot.add_cog(Cmds(bot))