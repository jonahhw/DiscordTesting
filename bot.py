# bot.py

import os
import env
from discord.ext import commands
import discord

TOKEN = env.DISCORD_TOKEN

bot = commands.Bot(command_prefix="rb ")

EmojiAssignments = {}

# Initialization message
@bot.event
async def on_ready():
    guilds = ', '.join([guild.name for guild in bot.guilds])
    print(f"{bot.user} is ready and connected to {guilds}.")

@bot.command(name="test", help=" - Boring command just for testing")
async def test_command(ctx):
    await ctx.send("You sent a !test")

@bot.command(name="assign", help=" - Assigns an emoji to a role\nUsage: rolebot assign [emoji] [role name]")
async def assign_emoji(ctx, emoji, roleString):
    role = discord.utils.find(lambda r: r.name == roleString, ctx.guild.roles)
    if not role:
        await ctx.send(f"{roleString} is not a valid role. Assignment of {emoji} has not changed.")
    PreviousRole = None
    if emoji in EmojiAssignments:
        PreviousRole = EmojiAssignments[emoji]
    EmojiAssignments[emoji] = role
    if PreviousRole:
        await ctx.send(f"Reassigning {emoji} from {PreviousRole.name} to {EmojiAssignments[emoji].name}")
    else:
        await ctx.send(f"{emoji} asssigned to {EmojiAssignments[emoji].name}")

@bot.command(name="detach", help=" - Removes the association from an emoji to a role\nUsage: rolebot detach [emoji_]")
async def detach_emoji(ctx, emoji):
    PreviousRole = None
    if emoji in EmojiAssignments:
        PreviousRole = EmojiAssignments[emoji]
        EmojiAssignments.pop(emoji)
    if PreviousRole:
        await ctx.send(f"{emoji} is no longer assigned to {PreviousRole.name}")
    else:
        await ctx.send(f"{emoji} was not assigned")

@bot.event
async def on_reaction_add(reaction, user):
    if (reaction.message.author != bot.user) or (reaction.emoji not in EmojiAssignments):
        return
    await user.add_roles(EmojiAssignments[reaction.emoji], reason="RoleBot")
    print(f"{user.name} given role {EmojiAssignments[reaction.emoji].name}")
    print(f"{reaction.emoji}")

@bot.event
async def on_reaction_remove(reaction, user):
    if (reaction.message.author != bot.user) or (reaction.emoji not in EmojiAssignments):
        return
    if EmojiAssignments[reaction.emoji] not in user.roles:
        print(f"{user.name} did not have role {EmojiAssignments[reaction.emoji].name}")
        return
    await user.remove_roles(EmojiAssignments[reaction.emoji], reason="RoleBot")
    print(f"{user.name} lost role {EmojiAssignments[reaction.emoji].name}")

@bot.event
async def on_error(event, *args, **kwargs):
    raise


bot.run(TOKEN)
