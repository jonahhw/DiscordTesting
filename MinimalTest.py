# MinimalTest.py

import env
from discord.ext import commands
import discord

TOKEN = env.DISCORD_TOKEN

bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    print("Ready")

@bot.command(name="test")
async def test(ctx):
    await ctx.send("Test recieved")
    
bot.run(TOKEN)
