import discord
from discord.ext import commands
import datetime

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
    embed = discord.Embed(colour=discord.Colour.blue())
    embed.add_field(name="Bot Invite",value="[Invite](https://discordapp.com/api/oauth2/authorize?client_id=484204301862830090&permissions=-1&scope=bot)")
    await ctx.send(embed=embed)
  
  @commands.command()
  async def google(self,ctx,*args):
      x = f"https://www.google.com/search?rlz=1C1CHBF_enUS753US753&ei=n62RW536KpL2swWl1IKIBg&q={args}&oq=google+search&gs_l=psy-ab.3..0i71l8.0.0..8290...0.0..0.0.0.......0......gws-wiz.vtjc2PzIHFg"
      y = x.replace(" ","+")
      await ctx.send(y)
      
  @commands.command()
  async def youtube(self,ctx,*args):
      x = f"https://www.youtube.com/results?search_query={args}"
      y = x.replace(" ","+")
      await ctx.send(y)
      
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
'''
  @commands.command()
  async def roles(self,ctx):
    await ctx.send(guild.roles)
'''
def setup(bot):
    bot.add_cog(User(bot))