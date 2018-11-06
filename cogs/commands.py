import ast
import asyncio
import collections
import contextlib
import copy
import discord
import importlib
import io
import inspect
import logging
import os
import pprint
import re
import shutil
import sqlite3
import sys
import time
import traceback
import datetime

from discord.ext import commands

"""
The first bot of Project X. This bot has multiple features:
+Custom Suggestions
+Moderation
+Economy
+Utility
+Custom Prefix
+Other commands
+Custom Pagination
Previous Owner: The Alchemist, started a bot. Recently, Alchemist has gone away, leaving his three trusted admins:
Arune: A coder of many wonders he has helped out people better than anyone has before in project x. Sadly He has left project x to finish his school life.
Crystal: Coming in at the top 2, Crystal has a sweet personality. She is creative, smart, and helpful. She lingers here and there, but she is like dessert, you can't miss her when she is there
Justin: The leader of the pack, Justin has put the most effort and time into the server and the bot. While he can be stubborn, he is also super helpful. A former mod of sebi, this guy is known for his many "Talents".
"""
conn = sqlite3.connect("database.db")
c = conn.cursor()

class User:

  def __init__(self,bot):
    self.bot = bot

  @commands.command(pass_context=True,brief="Lists Server Info | Usage: a!serverinfo | No Permission Limit")
  async def serverinfo(self,ctx):
        '''Get the server info'''
        guild = ctx.guild
        embed = discord.Embed(title=f'''{guild}''', colour=discord.Colour.blue(), description='More Info Below', timestamp = datetime.datetime.utcnow())
        embed.set_thumbnail(url=f'''{guild.icon_url}''')
        embed.add_field(name='Server Created At :', value=f'''  {guild.created_at}''', inline=False)
        embed.add_field(name='Created by :', value=f'''{guild.owner.mention}''',inline=False)
        embed.add_field(name='Region :', value=f'''  {guild.region}''',inline=False)
        embed.add_field(name='Server ID :', value=f'''<@{guild.id}>''',inline=False)
        embed.add_field(name='Server Members :', value=f'''  {len(guild.members)}''', inline=False)
        embed.add_field(name='Online Members :',value=f'''{len([I for I in guild.members if I.status is discord.Status.online])}''',inline=False)
        embed.add_field(name='Server Channel :', value=f'''  {len(guild.channels)}''', inline=False)
        await ctx.send(embed=embed)
  
  @commands.command(pass_context=True,brief="Lists User Info | Usage: a!user <user> | No Permission Limit")
  async def user(self, ctx, user: discord.Member):
      user = user or ctx.message.author
      embed = discord.Embed(title=f"{user.name}'s info", description="Here's what I could find:", color=0x00ff00)
      embed.add_field(name="Name", value=user.name, inline=True)
      embed.add_field(name="ID", value=user.id, inline=True)
      embed.add_field(name="Status", value=user.status, inline=True)
      embed.add_field(name="Created At",value=user.created_at.strftime('%B %d, %Y %I:%M %p'), inline=True)
      embed.add_field(name="Joined at", value=user.joined_at.strftime('%B %d, %Y %I:%M %p'))
      embed.add_field(name="Highest role", value=user.top_role)
      embed.set_thumbnail(url=user.avatar_url)
      await ctx.send(embed=embed)

  @commands.command(pass_context=True,brief="Lists  User Avatar | Usage: a!avatar <user> | No Permission Limit")
  async def avatar(self,ctx, user : discord.Member = None):
      user = user or ctx.message.author
      embed = discord.Embed(title=f'{user.name}\'s Avatar', description=f'I think I found {user.name}\'s Avatar but can\'t be too sure ;) Here you go!', colour=discord.Colour(0x0bc5df))
      embed.set_image(url=user.avatar_url)
      await ctx.send(embed=embed)

  @commands.command(brief="Lists Support Server for making bots | Usage: a!server | No Permission Limit")
  async def server(self,ctx):
    embed = discord.Embed(title="Server Info and Invite",description="```[Welcome to Project X]\n\nIn the server, you are able to learn the basics, as well as the advanced options, to creating your own Discord Bot. Here, you can give help, but also get help. Message an admin or higher to get your own bot in the server, which would allow you to share your bot, as well as test it with other developers\n\nOf course, we have rules, but unlike other servers, they are light and as long as you don't abuse the strict ones, you are fine.\n\nCome on over and enjoy a world of many wonders.}\n\n[Server invite]\n#https://discord.gg/MjxqTwf```")
    await ctx.send(embed=embed)


  @commands.command(brief = 'Shows owner of the server')
  async def owner(self, ctx):
    await ctx.send(f"{ctx.guild.owner.mention} owns this server")

  @commands.command(brief="Shows a dancing anime human | Usage: a!dance | No Permssion Limit")
  async def dance(self,ctx):
    embed=discord.Embed()
    embed.set_image(url="https://media.discordapp.net/attachments/462497054430593035/493287977552969735/Konosuba_dbab24_6194110.gif")
    await ctx.send(embed=embed)

  @commands.command(brief="Lists the ping | Usage: a!ping | No Permission Limit")
  async def ping(self,ctx):
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


  @commands.command(brief="Lets user suggest new things | Usage: a!suggest <suggestion(s)> | No Permisson Limit")
  async def suggest(self,ctx, *, msg):
    x = ctx.bot.get_channel(504616232981626880)
    embed = discord.Embed(title="Suggestion",description=f"{ctx.author.name} | ID : {ctx.author.id} | has sent suggestion | {msg}")
    await x.send(embed=embed)
    em = discord.Embed(title="Suggestion sent",description=f"Message was sent")
    await ctx.send(embed=em)

  @commands.command(brief="Lists the github link of the bot | Usage: a!github | No Permission Limit")
  async def github(self,ctx):
    embed = discord.Embed(title="Github Link",description="[Project X](https://github.com/ProjectXTeam/Alchemex/)",color=0x00FF00)
    await ctx.send(embed=embed)
    
  @commands.command(brief="Lists Bot Count, User Count and Total | Usage: a!count | No Permission Limit")
  async def count(self,ctx):
    bots = 0
    members = 0
    total = 0
    for x in ctx.guild.members:
     if x.bot == True:
        bots += 1
        total += 1
     else:
        members += 1
        total += 1
    embed = discord.Embed(title="Server Member Count",color=0x0000FF)
    embed.add_field(name="Bot Count",value=bots)
    embed.add_field(name="Member Count",value=members)
    embed.add_field(name="Total",value=total)
    await ctx.send(embed=embed)

class Moderator:

  def __init__(self,bot):
    self.bot = bot

  @commands.has_permissions(manage_roles=True)
  @commands.command(brief="Gives a user a role | Usage: a!giverole <user> <role> | Manage Roles Needed")
  async def giverole(self,ctx, member: discord.Member, xrole: discord.Role):
    await member.add_roles(xrole)

  @commands.has_permissions(manage_roles=True)
  @commands.command(brief="Takes a user's role | Usage: a!takerole <user> <role> | Manage Roles Needed")
  async def takerole(self,ctx, member: discord.Member, xrole: discord.Role):
    await member.remove_roles(xrole)

  @commands.has_permissions(ban_members=True)
  @commands.command(brief="Unbans a user | Usage: a!unban <user_id> | Ban Members Needed")
  async def unban(self,ctx,user: discord.Member):
    await ctx.guild.unban(user)
    await ctx.send(embed = discord.Embed(title="Unban",description="{0.name} got unbanned from the server".format(user)))

  @commands.has_permissions(kick_members=True)
  @commands.command(brief="Kicks Member | Usage: a!kick <user> | Kick Members Needed")
  async def kick(self,ctx, member: discord.Member,*reason): 
    await ctx.guild.kick(member)
    if reason == None:
      await ctx.send(embed = discord.Embed(title="User Kicked",description=f"Moderator: {ctx.author.mention} kicked {member.mention} from the server for no reason",color=0xFF0000)) 
    else:
      await ctx.send(embed = discord.Embed(title="User Kicked",description=f"{member.name} got kicked from the server for {reason}",color=0xFF0000))

  @commands.has_permissions(ban_members=True)
  @commands.command(brief="Bans a user | Usage: a!ban <user_id> | Ban Members Needed")
  async def ban(self,ctx, user: discord.Member,*reason):
    await ctx.guild.ban(user)
    if reason == None:
      await ctx.send(embed = discord.Embed(title="User Banned",description=f"Moderator: {ctx.author.mention} banned {user.mention} from the server for no reason",color=0xFF0000)) 
    else:
      await ctx.send(embed = discord.Embed(title="User Banned",description=f"{user.name} got kicked from the server for {reason}",color=0xFF0000))

  @commands.has_permissions(manage_messages=True)
  @commands.command(brief="Deletes X amount of messages | Usage: a!purge <# of messages> | Manage Messages Needed")
  async def purge(self,ctx, number: int = None):

    
    deleted = await ctx.channel.purge(
      limit = number + 1
      )

    await ctx.send(f'Deleted {len(deleted)} message(s)', delete_after=15)


  @commands.has_permissions(ban_members=True)
  @commands.command(brief="Sets the servers prefix, Do <Alchemex Prefix> to get current prefix | Usage: a!setprefix <prefix> | Ban Members Needed")
  async def setprefix(self,ctx,theprefix):
      x = c.execute("SELECT prefix FROM my_prefix WHERE guild_id=?",(ctx.guild.id,)).fetchall()
      if x != [] or None:
        c.execute("UPDATE my_prefix SET prefix = ? WHERE guild_id = ?",(theprefix,ctx.guild.id))
        conn.commit()
      else:
        c.execute("INSERT INTO my_prefix VALUES(?,?)",(theprefix,ctx.guild.id))
        conn.commit()

      await ctx.send(f"Your prefix is now {theprefix}")

  @commands.command(brief = 'shows people with administrator perms on the server', aliases =['mods', 'mod', 'admin', ])
  async def admins(self, ctx):
      embed = discord.Embed(description = f'Admins on {ctx.guild.name}',color=0x00ff00)
      for x in ctx.guild.members:
        if x.guild_permissions.administrator:
          embed.add_field(name = f'{x.display_name}', value = f"{x.name}#{x.discriminator}", inline = False)
      await ctx.send(embed = embed)



def setup(bot):
    bot.add_cog(User(bot))
    bot.add_cog(Moderator(bot))
