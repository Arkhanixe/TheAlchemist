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

  @commands.command(pass_context=True)
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
  
  @commands.command(pass_context=True)
  async def user(self,ctx, user: discord.Member):
      embed = discord.Embed(title="{}'s info".format(user.name), description="Here's what I could find:", color=0x00ff00)
      embed.add_field(name="Name", value=user.name, inline=True)
      embed.add_field(name="ID", value=user.id, inline=True)
      embed.add_field(name="Status", value=user.status, inline=True)
      embed.add_field(name="Created At",value=user.created_at, inline=True)
      embed.add_field(name="Joined at", value=user.joined_at)
      embed.add_field(name="Highest role", value=user.top_role)
      embed.set_thumbnail(url=user.avatar_url)
      await ctx.send(embed=embed)
 
  @commands.command(pass_context=True)
  async def avatar(self,ctx, user : discord.Member = None):
      user = user or ctx.message.author
      embed = discord.Embed(title=f'{user.name}\'s Avatar', description=f'I think I found {user.name}\'s Avatar but can\'t be too sure ;) Here you go!', colour=discord.Colour(0x0bc5df))
      embed.set_image(url=user.avatar_url)
      await ctx.send(embed=embed)

  @commands.command()
  async def server(self,ctx):
    embed = discord.Embed(title="Server Info and Invite",description="```[Welcome to Project X]\n\nIn the server, you are able to learn the basics, as well as the advanced options, to creating your own Discord Bot. Here, you can give help, but also get help. Message an admin or higher to get your own bot in the server, which would allow you to share your bot, as well as test it with other developers\n\nOf course, we have rules, but unlike other servers, they are light and as long as you don't abuse the strict ones, you are fine.\n\nCome on over and enjoy a world of many wonders.}\n\n[Server invite]\n#https://discord.gg/MjxqTwf```")
    await ctx.send(embed=embed)

  @commands.command()
  async def dance(self,ctx):
    embed=discord.Embed()
    embed.set_image(url="https://media.discordapp.net/attachments/462497054430593035/493287977552969735/Konosuba_dbab24_6194110.gif")
    await ctx.send(embed=embed)

  @commands.command()
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


  @commands.command()
  async def suggest(self,ctx, *, msg):
    x = ctx.bot.get_channel(493477736069726209)
    embed = discord.Embed(title="Suggestion",description=f"{ctx.author.name} | ID : {ctx.author.id} | has sent suggestion | {msg}")
    await x.send(embed=embed)
    em = discord.Embed(title="Suggestion sent",description=f"Message was sent")
    await ctx.send(embed=em)

  @commands.command()
  async def invite(self,ctx,botid,prefix):
    embed = discord.Embed(title="Bot Invite")
    c.execute("CREATE TABLE IF NOT EXISTS bots(Bot_ID BIGINT, Prefix VARCHAR,Author_ID BIGINT)")
    conn.commit()
    #Author
    embed.add_field(name=f"Author",value=f"{ctx.author.id} | {ctx.author}")
    embed.add_field(name=f"Invite",value=f"https://discordapp.com/api/oauth2/authorize?client_id={botid}&permissions=-1&scope=bot")
    embed.add_field(name=f"Prefix",value=f"{prefix}")
    embed.add_field(name=f"Guild",value=f"{ctx.guild}")
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

class Moderator:

  def __init__(self,bot):
    self.bot = bot

  @commands.has_permissions(manage_guild=True)
  @commands.command()
  async def promote(self,ctx, member: discord.Member, xrole: discord.Role):
    await member.add_roles(xrole)

  @commands.has_permissions(manage_guild=True)
  @commands.command()
  async def demote(self,ctx, member: discord.Member, xrole: discord.Role):
    await member.remove_roles(xrole)

  @commands.has_permissions(manage_guild=True)
  @commands.command()
  async def move(self,ctx,xrole: discord.Role,posx:int):
    newpos = await xrole.edit(position=posx)
    await ctx.author.send(newpos)

  @commands.has_permissions(ban_members=True)
  @commands.command()
  async def unban(self,ctx,user: discord.Member):
    await ctx.guild.unban(user)
    await ctx.send(embed = discord.Embed(title="Unban",description="{0.name} got unbanned from the server".format(user)))

  @commands.has_permissions(kick_members=True)
  @commands.command()
  async def kick(self,ctx, member: discord.Member,*reason): 
    await ctx.guild.kick(member)
    if reason == None:
      await ctx.send(embed = discord.Embed(title="User Kicked",description=f"Moderator: {ctx.author.mention} kicked {member.mention} from the server for no reason",color=0xFF0000)) 
    else:
      await ctx.send(embed = discord.Embed(title="User Kicked",description=f"{member.name} got kicked from the server for {reason}",color=0xFF0000))

  @commands.has_permissions(ban_members=True)
  @commands.command()
  async def ban(self,ctx, user: discord.Member,*reason):
    await ctx.guild.ban(user)
    if reason == None:
      await ctx.send(embed = discord.Embed(title="User Banned",description=f"Moderator: {ctx.author.mention} banned {member.mention} from the server for no reason",color=0xFF0000)) 
    else:
      await ctx.send(embed = discord.Embed(title="User Banned",description=f"{member.name} got kicked from the server for {reason}",color=0xFF0000))


  @commands.has_permissions(manage_messages=True)
  @commands.command()
  async def purge(self,ctx, number: int = None):

    
    deleted = await ctx.channel.purge(
      limit = number + 1
      )

    await ctx.send(
      'Deleted {} message(s)'.format(
        len(
          deleted
          )
        ), delete_after=15
      )

  @commands.has_permissions(administrator=True)
  @commands.command()
  async def setprefix(self,ctx,theprefix):
    x = c.execute("SELECT prefix FROM my_prefix WHERE guild_id=?",(ctx.guild.id,)).fetchall()
    if x != [] or None:
      c.execute("UPDATE my_prefix SET prefix = ? WHERE guild_id = ?",(theprefix,ctx.guild.id))
      conn.commit()
    else:
      c.execute("INSERT INTO my_prefix VALUES(?,?)",(theprefix,ctx.guild.id))
      conn.commit()

    await ctx.send(f"Your prefix is now {theprefix}")

def setup(bot):
    bot.add_cog(User(bot))
    bot.add_cog(Moderator(bot))
