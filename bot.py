# bot.py

import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} is connected to the following guilds:')
    for guild in client.guilds:
        print(f'  {guild.name} (id: {guild.id}), which has these members:')
        members = ', '.join([member.name for member in guild.members])
        print(f'    {members}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    print(f'{str(message.author)}: {message.content}')
    if message.content == "test":
        await message.channel.send("You sent a test")
    elif message.content == "raise-exception":
        raise discord.DiscordException

@client.event
async def on_error(event, *args, **kwargs):
    with open("err.log", "a+") as f:
        if event == "on_message":
            f.write(f"unhandled message written by {args[0].author.name} at {args[0].created_at}\n")
            f.write(f"  Full data: {args[0]}\n")
        else:
            raise


client.run(TOKEN)
