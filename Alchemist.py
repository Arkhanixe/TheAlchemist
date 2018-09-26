import discord
import sqlite3
from discord.ext import commands
import random
import datetime
from datetime import datetime
from some_paginator import Paginator
import time
import os

# Set up logging

extensions = {
'cogs.cmds',
"cogs.commands",
"cogs.admin",
"cogs.REPL",
"cogs.help"
}   # add more here later


"""def get_prefix(bot, message):
#    """#A callable Prefix for our bot. This could be edited to allow per server prefixes."""

    # Notice how you can use spaces in prefixes. Try to keep them simple though.
   # prefixes = ['>?', 'lol ', '!?']

    # Check to see if we are outside of a guild. e.g DM's etc.
   # if not message.guild:
        # Only allow ? to be used in DMs
       # return '?'
conn = sqlite3.connect("database.db")
c = conn.cursor()

def get_prefix(bot,ctx):
	if not ctx.guild:
		return "a!"
	else:
		xprefix = c.execute("SELECT prefix FROM my_prefix WHERE guild_id = ?",(ctx.guild.id,)).fetchall()
		if xprefix == None:
			return "a!"
		if xprefix == []:
			return "a!"
		else:
			return xprefix[0]

bot = commands.Bot(command_prefix=(get_prefix))
bot.launch_time = datetime.utcnow()
bot.remove_command("help")

@bot.command()
async def server(ctx):
	embed = discord.Embed(title="Server Invite",description="***The Alchemist Workshop***\nThe Alchemist Workshop is a server that helps people learn about bots. We are starting up right now but we will build ourselves up! We are encourage helpfulness as well as becoming an ally with other people in the community.\n\n***We Offer***:\n- Helping make discord bots\n- Language tutorials\n- Custom economy system\n- Server is made how the users want it to be made\n- Self promotion\n\n***Invite Link***:\n\nhttps://discord.gg/57cTcAA\n\n***Bot Invite***\n\nhttps://discordapp.com/api/oauth2/authorize?client_id=484204301862830090&permissions=-1&scope=bot\n")
	await ctx.send(embed=embed)

@bot.command()
async def dance(ctx):
	embed=discord.Embed()
	embed.set_image(url="https://media.discordapp.net/attachments/462497054430593035/493287977552969735/Konosuba_dbab24_6194110.gif")
	await ctx.send(embed=embed)

@bot.command()
@commands.is_owner()
async def dm(ctx, id: discord.User, message):
	embed = discord.Embed(title="Message",description=f"Dear User. You have a message. Here it is: \n {message}")
	await id.send(embed=embed)

@bot.command(aliases=["ut"])
async def uptime(ctx):
    delta_uptime = datetime.utcnow() - bot.launch_time
    hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)
    embed = discord.Embed(color=0x0000FF)
    embed.add_field(name="Alchemist Uptime", value=f"Weeks: **{weeks}**\nDays: **{days}**\nHours: **{hours}**\nMinutes: **{minutes}**\nSeconds: **{seconds}**")
    await ctx.send(embed=embed)

@bot.command()
async def remmes(ctx, number: int = None):
      if ctx.author.id != 462351034384252938:
        return False
        
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

@bot.command()
async def ping(ctx):
    # Time the time required to send a message first.
    # This is the time taken for the message to be sent, awaited, and then 
    # for discord to send an ACK TCP header back to you to say it has been
    # received; this is dependant on your bot's load (the event loop latency)
    # and generally how shit your computer is, as well as how badly discord
    # is behaving.
    start = time.monotonic()
    msg = await ctx.send('Pinging...')
    millis = (time.monotonic() - start) * 1000

    # Since sharded bots will have more than one latency, this will average them if needed.
    heartbeat = ctx.bot.latency * 1000

    await msg.edit(content=f'Heartbeat: {heartbeat:,.2f}ms\tACK: {millis:,.2f}ms.')

@bot.command()
async def save(ctx,*args):
	with open("Desktop/Alchemistsaved.txt","a") as f:
		f.write(args[0])
		f.write("\n\n")

@bot.command()
async def suggest(ctx, *, msg):
    x = ctx.bot.get_channel(493477736069726209)
    embed = discord.Embed(title="Suggestion",description=f"{ctx.author.name} | ID : {ctx.author.id} | has sent suggestion | {msg}")
    await x.send(embed=embed)
    em = discord.Embed(title="Suggestion sent",description=f"Message was sent")
    await ctx.send(embed=em)

@bot.listen()
async def on_message(message):
	"""if message.guild.me in message.mentions:
		xprefix = c.execute("SELECT prefix FROM my_prefix WHERE guild_id = ?",(message.guild.id,)).fetchall()
		y = xprefix[0]
		await message.channel.send(f"You probaly want my prefix! Here you go: {y[0]}")
	"""
	if isinstance(message.channel, discord.DMChannel):
			channelid = bot.get_channel(493774930169823242)
			em_dm = discord.Embed(colour=0x0000FF)
			em_dm.set_author(name=f"Message ID: {message.id}",icon_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRtcb5rrDHigYWUiULXW4plUlUI-4w4-wVtL8PpU8Bbg4ejnFBhgg")
			em_dm.add_field(name="Content",value=f"{message.content}")
			em_dm.set_footer(text=f"Sent by {message.author} | ID = {message.author.id}")
			await channelid.send(embed=em_dm)

	if message.content.startswith("Alchemist prefix"):
		xprefix = c.execute("SELECT prefix FROM my_prefix WHERE guild_id = ?",(message.guild.id,)).fetchall()
		await message.channel.send(xprefix[0])


@bot.event
async def on_command_error(ctx,error):
	embed = discord.Embed(title="Command Error",description=error)
	print(error)

@bot.command()
async def setprefix(ctx,theprefix):
	x = c.execute("SELECT prefix FROM my_prefix WHERE guild_id=?",(ctx.guild.id,)).fetchall()
	if x != [] or None:
		c.execute("UPDATE my_prefix SET prefix = ? WHERE guild_id = ?",(theprefix,ctx.guild.id))
		conn.commit()
	else:
		c.execute("INSERT INTO my_prefix VALUES(?,?)",(theprefix,ctx.guild.id))
		conn.commit()

	await ctx.send(f"Your prefix is now {theprefix}")

@bot.command()
async def invite(ctx,botid,prefix):
	embed = discord.Embed(title="Bot Invite")
	c.execute("CREATE TABLE IF NOT EXISTS bots(Bot_ID BIGINT, Prefix VARCHAR,Author_ID BIGINT)")
	conn.commit()
	#Author
	embed.add_field(name=f"Author",value=f"{ctx.author.id} | {ctx.author}")
	embed.add_field(name=f"Invite",value=f"https://discordapp.com/api/oauth2/authorize?client_id={botid}&permissions=-1&scope=bot")
	embed.add_field(name=f"Prefix",value=f"{prefix}")
	y = c.execute("SELECT * FROM bots WHERE Bot_ID=?",(botid))
	if y != [] or None:
		pass
	else:
		c.execute("INSERT INTO bots VALUES(?,?,?)",(botid,prefix,ctx.author.id))
		conn.commit()
	em = discord.Embed(description="Thank you for submitting your bot! You should get a dm within the next 24 hours if your bot has been accepted! Have a good day!")
	await ctx.send(em)
	x = ctx.bot.get_channel(494282311400030209)
	await x.send(embed=embed)

# If we fail to load an extension, we just leave it out.
for extension in extensions:
	try:
		bot.load_extension(extension)
	except Exception as e:
		print(e)

@bot.event
async def on_command_completion(ctx):
	try:
		await ctx.message.delete()
	except:
		pass

@commands.is_owner()
@bot.command()
async def restart(ctx):
	with open("Token.txt") as fp:
		token = fp.read().strip()

	bot.run(token)


@bot.event
async def on_ready():
	print(f"Logged in as {bot.user.name}")
	print(f"ID : {bot.user.id}")
	print(f"Preparing Game")
	game = discord.Game(f" Nothing | Guild Count: {len(bot.guilds)}")
	await bot.change_presence(status=discord.Status.online,activity=game)
	print(f"Playing {game}")

@bot.event
async def on_member_join(member: discord.Member):
  if member.guild.id != 494277342307549184:
  	return False

  embed=discord.Embed(timestamp = datetime.utcnow())
  embed.add_field(name="Name",value=f"{member} has joined",inline=True)
  embed.add_field(name="Creation",value=member.created_at,inline=True)
  embed.color: 3447003
  embed.set_thumbnail(url=member.avatar_url)
  general_channel = bot.get_channel(494277342307549186)
  logs = bot.get_channel(494281418894213151)
  general_channel.send(embed=embed)
  logs.send(embed=embed)

@bot.event
async def on_member_join(member: discord.Member):

  embed=discord.Embed(timestamp = datetime.utcnow())
  embed.add_field(name="Name",value=f"{member} has joined",inline=True)
  embed.add_field(name="Creation",value=member.created_at,inline=True)
  embed.add_field(name="Guild",value=member.guild.name,inline=True)
  embed.color: 3447003
  embed.set_thumbnail(url=member.avatar_url)
  general_channel = bot.get_channel(494277342307549186)
  logs = bot.get_channel(494281418894213151)
  await general_channel.send(embed=embed)
  await logs.send(embed=embed)

@bot.event
async def on_member_leave(member: discord.Member):

  embed=discord.Embed(timestamp = datetime.utcnow())
  embed.add_field(name="Name",value=f"{member} has left",inline=True)
  embed.add_field(name="Creation",value=member.created_at,inline=True)
  embed.add_field(name="Joined",value=member.joined_at,inline=True)
  embed.add_field(name="Guild",value=member.guild.name,inline=True)
  embed.color: 3447003
  embed.set_thumbnail(url=member.avatar_url)
  general_channel = bot.get_channel(494277342307549186)
  logs = bot.get_channel(494281418894213151)
  await general_channel.send(embed=embed)
  await logs.send(embed=embed)
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
"""
@bot.group(invoke_without_command=True)
async def help(ctx):
	for command in bot.commands:
		em = discord.Embed(title="Alchemist Help Menu",description=command_S)
		await ctx.send(embed = em)
		
"""
with open("Token.txt") as fp:
    token = fp.read().strip()

bot.run(token)

#Omega Cafe
#bot.run("NDM0MTMyOTA1NDgwOTQ1Njc0.DhOAow.Zj5Kzkv_n-NjjPq8bQQWxMh2Kr0")
