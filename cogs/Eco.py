import discord
import asyncio
import datetime
import time
import os
import random
import sqlite3

from discord.ext import commands

class Economy:
	
	def __init__(self,bot):
		self.bot = bot
		
	@commands.command()
	async def register(self,ctx):
		c.execute("INSERT INTO bank VALUES(?, ?, ?, ?, ?)",(ctx.author.id, 1.0 , 1, ctx.author.name , "extra"))
		conn.commit()

	#@commands.cooldown(1, 30, commands.BucketType.user)
	@commands.command()
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

	@commands.command()
	async def bal(self,ctx):
		Balance = c.execute("SELECT Balance FROM bank WHERE User_ID = ?",(ctx.author.id,)).fetchall()
		n = Balance[0]
		m = n[0]
		em = discord.Embed(title=f"{ctx.author.name}, your balance is:",description=f"${m}")
		await ctx.send(embed=em)

	@commands.command()
	async def top(self,ctx):
		Alpha = c.execute("SELECT * FROM bank ORDER BY balance DESC").fetchall()
		await ctx.send(Alpha[:10])

	@commands.group(invoke_without_command=True)
	async def buy(self,ctx):
		pass

	@buy.command(name = "ship")
	async def buy_ship(self,ctx):
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

def setup(bot):
	bot.add_cog(Economy(bot))
