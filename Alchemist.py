import discord
import sqlite3
from discord.ext import commands
import random

# Set up logging

extensions = {
'cogs.cmds',
"cogs.commands",
"cogs.admin"
}   # add more here later

bot = commands.Bot(command_prefix='a!')

# If we fail to load an extension, we just leave it out.
for extension in extensions:
	try:
		bot.load_extension(extension)
	except Exception as e:
		print(e)

@bot.event
async def on_command_completion(ctx):
    await ctx.message.delete()

@bot.event
async def on_ready():
	print(f"Logged in as {bot.user.name}")
	print(f"ID : {bot.user.id}")
	print(f"Preparing Game")
	game = discord.Game(" Nothing | Guild Count: 3")
	await bot.change_presence(status=discord.Status.online,activity=game)
	print(f"Playing {game}")

conn = sqlite3.connect("database.db")
c = conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS bank(User_ID BIGINT NOT NULL, Balance float)")
conn.commit()


@bot.command()
async def register(ctx):
	c.execute("INSERT INTO bank VALUES(?, ?)",(ctx.author.id, 0))
	conn.commit()

#@commands.cooldown(1, 30, commands.BucketType.user)
@bot.command()
async def work(ctx):
	Balance = c.execute("SELECT Balance FROM bank WHERE User_ID = ?",(ctx.author.id,)).fetchall()
	y = Balance[0]
	z = y[0]
	x = 1
	Boxed = (x *)+ z 
	c.execute("UPDATE bank SET balance=? WHERE user_id=?",(Boxed,ctx.author.id))
	conn.commit()

@bot.command()
async def balance(ctx):
	Balance = c.execute("SELECT Balance FROM bank WHERE User_ID = ?",(ctx.author.id,)).fetchall()
	await ctx.send(Balance)

@bot.command()
async def top(ctx):
	Alpha = c.execute("SELECT * FROM bank ORDER BY balance DESC").fetchall()
	await ctx.send(Alpha[:10])

bot.run("NDg0MjA0MzAxODYyODMwMDkw.DmemNw.AYqV7dtez3hf4j5mfcKB3r97Vdg")

#Omega Cafe
#bot.run("NDM0MTMyOTA1NDgwOTQ1Njc0.DhOAow.Zj5Kzkv_n-NjjPq8bQQWxMh2Kr0")
