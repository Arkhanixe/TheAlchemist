import discord
import datetime
from discord.ext import commands

def owner(ctx):
  if ctx.author.id == 462351034384252938:
    return True
  else:
    return False

class User:

  def __init__(self,bot):
    self.bot = bot

  @commands.command()
  async def invite(self,ctx):
    await ctx.send("https://discordapp.com/api/oauth2/authorize?client_id=484204301862830090&permissions=-1&scope=bot")

  @commands.check(owner)
  @commands.command()
  async def position(self,ctx,xrole: discord.Role):
    await ctx.author.send(xrole.position)

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
  async def roles(self,ctx):
    await ctx.send(guild.roles)

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

def setup(bot):
    bot.add_cog(User(bot))
    bot.add_cog(Moderator(bot))