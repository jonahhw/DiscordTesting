# bot.py

import os
import env
from discord.ext import commands
import discord

TOKEN = env.DISCORD_TOKEN       # The token, taken from env.py (which is hidden from the git repo)

bot = commands.Bot(command_prefix="rb ")

EmojiAssignments = {}   # A dictionary of dictionaries. EmojiAssignments[Channel][Emoji] = Role

# Initialization message
@bot.event
async def on_ready():
    guilds = ", ".join(guild.name for guild in bot.guilds)
    print(f"{bot.user} is ready and connected to {guilds}")

@bot.command(name="activate", help=" - Activates the bot in the channel in which it's run.")
async def activate(ctx):        # If it's not already there, it adds a dictionary under the channel in which this is run
    if ctx.channel not in EmojiAssignments:
        EmojiAssignments[ctx.channel] = {}
        await ctx.send(f"RoleBot is now active in {ctx.channel.name}")
    else:
        await ctx.send(f"RoleBot is already active in {ctx.channel.name}")

@bot.command(name="deactivate", help=" - Deactivates the bot in the channel in which it's run. Warning: this will delete all emoji associations")
async def deactivate(ctx):      # Removes the dectionary entry for this channel
    if ctx.channel in EmojiAssignments:
        EmojiAssignments.pop(ctx.channel)
        await ctx.send(f"RoleBot is no longer active in {ctx.channel.name}")

    else:
        await ctx.send(f"RoleBot was not active in {ctx.channel.name}")

@bot.command(name="assign", help=" - Assigns an emoji to a role. Usage: `rb assign [emoji] [role name]`")
async def assign_emoji(ctx, emoji, roleString):
    if ctx.channel not in EmojiAssignments:
        await ctx.send(f"RoleBot is not active in {ctx.channel.name}")
        return
    role = discord.utils.find(lambda r: r.name == roleString, ctx.guild.roles)
    if not role:
        await ctx.send(f"{roleString} is not a valid role. Assignment of {emoji} has not changed.")
        return
    PreviousRole = None
    if emoji in EmojiAssignments[ctx.channel]:
        PreviousRole = EmojiAssignments[ctx.channel][emoji]
    EmojiAssignments[ctx.channel][emoji] = role
    if PreviousRole:
        await ctx.send(f"Reassigning {emoji} from {PreviousRole.name} to {EmojiAssignments[ctx.channel][emoji].name}")
    else:
        await ctx.send(f"{emoji} asssigned to {EmojiAssignments[ctx.channel][emoji].name}")

@bot.command(name="deassign", help=" - Removes the association from an emoji to a role. Usage: `rb deassign [emoji]`")
async def deassign_emoji(ctx, emoji):
    if ctx.channel not in EmojiAssignments:
        await ctx.send(f"RoleBot is not active in {ctx.channel.name}")
        return
    PreviousRole = None
    if emoji in EmojiAssignments[ctx.channel]:
        PreviousRole = EmojiAssignments[ctx.channel][emoji]
        EmojiAssignments[ctx.channel].pop(emoji)
    if PreviousRole:
        await ctx.send(f"{emoji} is no longer assigned to {PreviousRole.name}")
    else:
        await ctx.send(f"{emoji} was not assigned")

@bot.event
async def on_reaction_add(reaction, user):
    cnl = reaction.message.channel
    if (cnl not in EmojiAssignments) or (reaction.message.author != bot.user) or (reaction.emoji not in EmojiAssignments[cnl]):
        return
    await user.add_roles(EmojiAssignments[cnl][reaction.emoji], reason="RoleBot")
    print(f"{user.name} given role {EmojiAssignments[cnl][reaction.emoji].name}")

@bot.event
async def on_reaction_remove(reaction, user):
    cnl = reaction.message.channel
    if (cnl not in EmojiAssignments) or (reaction.message.author != bot.user) or (reaction.emoji not in EmojiAssignments[cnl]):
        return
    if EmojiAssignments[cnl][reaction.emoji] not in user.roles:
        print(f"{user.name} did not have role {EmojiAssignments[cnl][reaction.emoji].name}")
        return
    await user.remove_roles(EmojiAssignments[cnl][reaction.emoji], reason="RoleBot")
    print(f"{user.name} lost role {EmojiAssignments[cnl][reaction.emoji].name}")

@bot.event
async def on_error(event, *args, **kwargs):
    raise


bot.run(TOKEN)
