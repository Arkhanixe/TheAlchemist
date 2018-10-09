import discord
import datetime
from discord.ext import commands
import sqlite3

"""
***Discord Tutorial Server***

***Alchemist's Tutorials for Peculiar Children***
The Alchemist Workshop is a server that helps people learn about bots. We are starting up right now but we will build ourselves up! We are encourage helpfulness as well as becoming an ally with other people in the community.
      
***We Offer***:
- Helping make discord bots
- Language tutorials
- Custom economy system
- Server is made how the users want it to be made
- Self promotion
- Also looking for tutorial writers of any language, discord or not

***Invite Link***:
https://discord.gg/jFeR6aE

***Bot Invite***
https://discordapp.com/api/oauth2/authorize?client_id=484204301862830090&permissions=-1&scope=bot


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
    embed = discord.Embed(title="Server Invite",description="***The Alchemist Workshop***\nThe Alchemist Workshop is a server that helps people learn about bots. We are starting up right now but we will build ourselves up! We are encourage helpfulness as well as becoming an ally with other people in the community.\n\n***We Offer***:\n- Helping make discord bots\n- Language tutorials\n- Custom economy system\n- Server is made how the users want it to be made\n- Self promotion\n\n***Invite Link***:\n\nhttps://discord.gg/57cTcAA\n\n***Bot Invite***\n\nhttps://discordapp.com/api/oauth2/authorize?client_id=484204301862830090&permissions=-1&scope=bot\n")
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
  async def unban(self,ctx,user: int):
    userid = discord.Object(user)
    await ctx.guild.unban(user=userid)

  @commands.has_permissions(kick_members=True)
  @commands.command()
  async def kick(self,ctx, member: discord.Member):	
    await ctx.guild.kick(member)
    await ctx.send(embed = discord.Embed(title="Kick",description="{0.name} got kicked from the server".format(member)))

  @commands.has_permissions(ban_members=True)
  @commands.command()
  async def ban(self,ctx, user: discord.Member):
    await ctx.guild.ban(user)
    await ctx.send(embed = discord.Embed(title="Ban",description="{0.name} got banned from the server".format(user)))

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
