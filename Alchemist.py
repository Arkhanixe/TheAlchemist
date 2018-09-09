import discord
import sqlite3
from discord.ext import commands
import random
import SECRETS
from SECRETS import TOKEN

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
	c.execute("INSERT INTO bank VALUES(?, ?, ?, ?, ?)",(ctx.author.id, 1.0 , 1, ctx.author.name , "extra"))
	conn.commit()

#@commands.cooldown(1, 30, commands.BucketType.user)
@bot.command()
async def work(ctx):
	Balance = c.execute("SELECT Balance FROM bank WHERE User_ID = ?",(ctx.author.id,)).fetchall()
	y = Balance[0]
	z = y[0]
	x = 1
	ships2 = c.execute("SELECT shipcount FROM bank WHERE User_ID = ?",(ctx.author.id,)).fetchall()
	ships1 = ships2[0]
	ships = ships1[0]
	Boxed = (5 * int(ships)) + int(z) 
	c.execute("UPDATE bank SET balance=? WHERE user_id=?",(int(Boxed),ctx.author.id))
	conn.commit()

@bot.command()
async def bal(ctx):
	Balance = c.execute("SELECT Balance FROM bank WHERE User_ID = ?",(ctx.author.id,)).fetchall()
	n = Balance[0]
	m = n[0]
	em = discord.Embed(title=f"{ctx.author.name}, your balance is:",description=f"${m}")
	await ctx.send(embed=em)

@bot.command()
async def top(ctx):
	Alpha = c.execute("SELECT * FROM bank ORDER BY balance DESC").fetchall()
	await ctx.send(Alpha[:10])

@bot.group(invoke_without_command=True)
async def buy(ctx):
	pass

@buy.command(name = "ship")
async def buy_ship(ctx):
	Balance = c.execute("SELECT Balance FROM bank WHERE User_ID = ?",(ctx.author.id,)).fetchall()
	ships = c.execute("SELECT shipcount FROM bank WHERE User_ID = ?",(ctx.author.id,)).fetchall()
	n = Balance[0]
	o = ships[0]
	m = n[0]
	p = o[0]
	if m >= 200 * p:
		z = m - 500 * p
		q = p + 1
		c.execute("UPDATE bank SET balance=? WHERE user_id=?",(z,ctx.author.id))
		conn.commit()
		c.execute("UPDATE bank SET shipcount=? WHERE user_id=?",(q,ctx.author.id))
		conn.commit()
	else:
		em = discord.Embed(title=ctx.author.name,description="You don't have enough money")
		await ctx.send(embed = em)

bot.run(TOKEN)

#Omega Cafe
#bot.run("NDM0MTMyOTA1NDgwOTQ1Njc0.DhOAow.Zj5Kzkv_n-NjjPq8bQQWxMh2Kr0")
