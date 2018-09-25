#Imports
import discord
#froms
from discord.ext import commands

bot = commands.Bot(command_prefix="un!",dm_help=True)

class Events:
	#Detects when the bot starts
	@bot.listen()
	async def on_ready():
		print(f" Username | {bot.user.name} \n ID | {bot.user.id} \n Server Count | {len(bot.guilds)}")
		game = discord.Game(f" youtube")
		await bot.change_presence(status=discord.Status.online,activity=game)

	#Loads commands
	extensions = {
		"cogs.youtube"
	}

	for extension in extensions:
		try:
			bot.load_extension(extension)
		except Exception as e:
			print(e)

def setup(bot):
	bot.add_cog(Events)

#Run Bot
bot.run("NDkzOTE5NjkxNjM1NTU2MzUy.Dor-eQ.HLigr_bSL3FschpXM0T8tAcYRxI")