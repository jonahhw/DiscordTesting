# bot.py

import os
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    print(f'{bot.user} is connected to the following guilds:')
    for guild in bot.guilds:
        print(f'  {guild.name} (id: {guild.id}), which has these members:')
        members = ', '.join([member.name for member in guild.members])
        print(f'    {members}')

@bot.command(name="test")
async def test_command(ctx):
    await ctx.send("You sent a !test")

@bot.event
async def on_error(event, *args, **kwargs):
    with open("err.log", "a+") as f:
        if event == "on_message":
            f.write(f"unhandled message written by {args[0].author.name} at {args[0].created_at}\n")
            f.write(f"  Full data: {args[0]}\n")
        else:
            raise


bot.run(TOKEN)
