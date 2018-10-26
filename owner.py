import discord
import traceback
import sqlite3

from discord.ext import commands

extensions = {
	"cogs.commands",
	#False "cogs.admin",
	"cogs.REPL",
	"cogs.help",
	#Broken "cogs.Eco",
	"cogs.emoji",
	"owner"
}  

class Owner:
	def __init__(self,bot):
	  self.bot = bot

	async def owner_check(ctx):
		owners = [293992072887795712,200686748458549248]
		return ctx.author.id in owners

	@commands.command(aliases=['load'])
	@commands.check(owner_check)
	async def loadcog(self,ctx,extension):
		async with ctx.typing():
			try:
				bot.load_extension(extension)
				await ctx.send(f":gear: Loaded {extension} :gear:",delete_after = 20)
			except:
				await ctx.send(f"Sorry {ctx.author.mention}, you can't run this command because you are not an Alchemex Creator",delete_after = 20)

	@commands.command(aliases=['unload'])
	@commands.check(owner_check)
	async def unloadcog(self,ctx,extension):
		async with ctx.typing():
			try:
				bot.unload_extension(extension)
				await ctx.send(f":gear: Unloaded {extension} :gear:",delete_after= 20)
			except:
				await ctx.send(f"Sorry {ctx.author.mention}, you can't run this command because you are not an Alchemex Creator",delete_after = 20)


	#allows you to update cogs without resetting bot
	@commands.command(aliases=['resetcogs', 'restartcogs', 'reloadall','reload'])
	@commands.check(owner_check)
	async def reloadcogs(self,ctx):
		async with ctx.typing():
			await ctx.send(":gear: Reloading all cogs!", delete_after = 10)
			for extension in extensions:
				bot.unload_extension(extension)
				bot.load_extension(extension)
				await ctx.send(f":gear: Successfully Reloaded {extension}", delete_after = 10)
		await ctx.send(":gear: Successfully Reloaded all cogs!",delete_after = 30)

def setup(bot):
    bot.add_cog(Owner(bot))
