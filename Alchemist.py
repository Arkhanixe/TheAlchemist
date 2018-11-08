import discord
import sqlite3
from discord.ext import commands
import random
import datetime
from datetime import datetime
#from some_paginator import Paginator
import time
import os

now = datetime.now()

# Set up logging

extensions = {
"cogs.commands",
#"cogs.REPL",
#"cogs.help",
"cogs.emoji",
'libneko.extras.help',
'libneko.extras.superuser'
}   # add more here later


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

async def owner_check(ctx):
	owners = [293992072887795712,200686748458549248]
	return ctx.author.id in owners

#allows you to update cogs without resetting bot
@bot.command(aliases=['resetcogs', 'restartcogs', 'reloadall','reloadcogs'],brief="Reloads all the cogs | Usage: a!reload | Only Only")
@commands.check(owner_check)
async def reload(ctx):
	async with ctx.typing():
		await ctx.send(":gear: Reloading all cogs!", delete_after = 10)
		for extension in extensions:
			bot.unload_extension(extension)
			bot.load_extension(extension)
			await ctx.send(f":gear: Successfully Reloaded {extension}", delete_after = 10)
	await ctx.send(":gear: Successfully Reloaded all cogs!",delete_after = 30)

@bot.listen()
async def on_message(message):
	"""if message.guild.me in message.mentions:
		xprefix = c.execute("SELECT prefix FROM my_prefix WHERE guild_id = ?",(message.guild.id,)).fetchall()
		y = xprefix[0]
		await message.channel.send(f"You probaly want my prefix! Here you go: {y[0]}")
	"""
	if isinstance(message.channel, discord.DMChannel):
		channelid = bot.get_channel(504616214237151243)
		em_dm = discord.Embed(colour=0x0000FF)
		em_dm.set_author(name=f"Message ID: {message.id}",icon_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRtcb5rrDHigYWUiULXW4plUlUI-4w4-wVtL8PpU8Bbg4ejnFBhgg")
		em_dm.add_field(name="Content",value=f"{message.content}")
		em_dm.set_footer(text=f"Sent by {message.author} | ID = {message.author.id}")
		await channelid.send(embed=em_dm)

	if message.content.startswith("Alchemex prefix"):
		xprefix = c.execute("SELECT prefix FROM my_prefix WHERE guild_id = ?",(message.guild.id,)).fetchall()
		await message.channel.send(xprefix[0])
	
# If we fail to load an extension, we just leave it out.
for extension in extensions:
	try:
		bot.load_extension(extension)
	except Exception as e:
		print(e)

@bot.event
async def on_ready():
	print(f"Logged in as {bot.user.name}")
	print(f"ID : {bot.user.id}")
	print(f"Discrim: {bot.user.discriminator}")
	print(f"Is Bot? {bot.user.bot}")
	print(f"Email: {bot.user.email}")
	print(f"Have premium? {bot.user.premium}")
	print(f"Preparing Game")
	game = discord.Game(f" Nothing | User Count: {len(bot.guilds)}")
	await bot.change_presence(status=discord.Status.online,activity=game)
	print(f"Playing {game}")

c.execute("CREATE TABLE IF NOT EXISTS bank(User_ID BIGINT NOT NULL, Balance float)")
conn.commit()


@bot.listen()
async def on_member_join(member):
	if member.bot == False:
		embed = discord.Embed(title=f"{member.name}#{member.discriminator}",color=0x009933)
		embed.add_field(name=f"Creation Date",value=f" {member.created_at.strftime('%B %d, %Y')}",inline=True)
		embed.add_field(name=f"Join Date", value=f" {member.joined_at.strftime('%B %d, %Y')}",inline=True)
		embed.add_field(name=f"Member Count", value=f" {member.guild.member_count}")
		embed.set_author(name="Member Joined",icon_url=member.avatar_url)
		try:
			channel = discord.utils.get(member.guild.channels, name="join-leaves")
			await channel.send(embed=embed)
			role = discord.utils.get(member.guild.roles, name="Alchemex Members")
			await member.add_roles(role)
		except:
			channel = discord.utils.get(member.guild.channels, name="general")
			await channel.send(embed=embed)
			role = discord.utils.get(member.guild.roles, name="Alchemex Members")
			await member.add_roles(role)
	else:
		embed = discord.Embed(title=f"BOT {member.name}#{member.discriminator}",color=0x009933)
		embed.add_field(name=f"Creation Date",value=f" {member.created_at.strftime('%B %d, %Y')}",inline=True)
		embed.add_field(name=f"Join Date", value=f" {member.joined_at.strftime('%B %d, %Y')}",inline=True)
		embed.set_author(name="Member Joined",icon_url=member.avatar_url)
		try:
			channel = discord.utils.get(member.guild.channels, name="join-leaves")
			await channel.send(embed=embed)
			role = discord.utils.get(member.guild.roles, name="Alchemex Members")
			await member.add_roles(role)
		except:
			channel = discord.utils.get(member.guild.channels, name="general")
			await channel.send(embed=embed)
			role = discord.utils.get(member.guild.roles, name="Alchemex Members")
			await member.add_roles(role)

@bot.listen()
async def on_member_remove(member):
        if member.bot == False:
            embed = discord.Embed(title=f"{member.name}#{member.discriminator}",color=0xff0000)
            embed.add_field(name=f"Join Date", value=f" {member.joined_at.strftime('%B %d, %Y')}",inline=True)
            embed.add_field(name=f"Leave Date", value=f" {now.strftime('%B %d, %Y')}",inline=True)
            embed.add_field(name=f"Member Count", value=f" {member.guild.member_count}")
            embed.set_author(name="Member Left",icon_url=member.avatar_url)
            try:
                channel = discord.utils.get(member.guild.channels, name="join-leaves")
                await channel.send(embed=embed)
            except:
                channel = discord.utils.get(member.guild.channels, name="general") 
                await channel.send(embed=embed)
        else:
            embed = discord.Embed(title=f"BOT {member.name}#{member.discriminator}",color=0xff0000)
            embed.add_field(name=f"Join Date", value=f" {member.joined_at.strftime('%B %d, %Y')}",inline=True)
            embed.add_field(name=f"Leave Date", value=f" {now.strftime('%B %d, %Y')}",inline=True)
            embed.set_author(name="Member left",icon_url=member.avatar_url)
            try:
                channel = discord.utils.get(member.guild.channels, name="join-leaves")
                await channel.send(embed=embed)
            except:
                channel = discord.utils.get(member.guild.channels, name="general") 
                await channel.send(embed=embed)



@bot.listen()
async def on_guild_join(guild):
	embed = discord.Embed(Title="Joined Guild",description=f"Thank you for inviting me! My name is Alchemex. My prefix is <a!>. My help server is a!server. Have a nice day! \nAlchemex Creators")
	channel = discord.utils.get(guild.channels, name="general")
	await channel.send(embed=embed)

with open("Token.txt") as fp:
    token = fp.read().strip()

bot.run(token)

