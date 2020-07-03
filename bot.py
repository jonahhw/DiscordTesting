# bot.py

import os
import env
from discord.ext import commands
import discord
import json

TOKEN = env.DISCORD_TOKEN       # The token, taken from env.py (which is hidden from the git repo)
NOT_ACTIVE_MESSAGE = "RoleBot is not active in {channel_name}. Use `rb activate` to activate."
SAVE_FILE = "save.json"
ROLE_NEEDED = "MasterOfRoles"   # Change this to @everyone if you want anyone to be able to assign emoji and stuff

bot = commands.Bot(command_prefix="rb ")

EmojiAssignments = {}   # A dictionary of dictionaries. EmojiAssignments[Channel][Emoji] = Role

# Initialization message
@bot.event
async def on_ready():
    SavableAssignments = {}
    try:
        with open(SAVE_FILE, "r") as f:
            SavableAssignments = json.load(f)
    except:
        print(f"Could not load file {SAVE_FILE}")
    else:
        for cnl_id in SavableAssignments:
            cnl = None
            guild = None
            for guild_it in bot.guilds:
                for channel in guild_it.text_channels:
                    if channel.id == int(cnl_id):
                        cnl = channel
                        guild = guild_it
            if cnl:
                EmojiAssignments[cnl] = {}
                for emoji in SavableAssignments[cnl_id]:
                    EmojiAssignments[cnl][emoji] = discord.utils.get(guild.roles, id=int(SavableAssignments[cnl_id][emoji]))
    #######################
    guilds = ", ".join(guild.name for guild in bot.guilds)
    print(f"{bot.user} is ready and connected to {guilds}")

@bot.command(name="list", help=" - Lists the emoji and their corresponding roles")
async def list_emoji(ctx):
    if ctx.channel not in EmojiAssignments:
        await ctx.send(NOT_ACTIVE_MESSAGE.format(channel_name = ctx.channel.name))
        return
    message_text = "Current bindings:"
    for emoji in EmojiAssignments[ctx.channel]:
        message_text += f"\n{emoji}: {EmojiAssignments[ctx.channel][emoji].name}"
    message = await ctx.send(message_text)
    for emoji in EmojiAssignments[ctx.channel]:
        try:
            await message.add_reaction(emoji)
        except discord.errors.HTTPException:
            await ctx.send(f"Something went wrong when reacting with \"{emoji}\". Are you sure it's an emoji?")
        except:
            raise

@list_emoji.error
async def list_error(ctx, error):
    if not await general_error(ctx, error): raise

@bot.command(name="activate", help=" - Activates the bot in the channel in which it's run.")
@commands.check_any(commands.has_role(ROLE_NEEDED), commands.has_permissions(manage_roles=True))
async def activate(ctx):        # If it's not already there, it adds a dictionary under the channel in which this is run
    if ctx.channel not in EmojiAssignments:
        EmojiAssignments[ctx.channel] = {}
        await ctx.send(f"RoleBot is now active in {ctx.channel.name}")
    else:
        await ctx.send(f"RoleBot is already active in {ctx.channel.name}")

@activate.error
async def activate_error(ctx, error):
    if not await general_error(ctx, error): raise

@bot.command(name="deactivate", help=" - Deactivates the bot in the channel in which it's run. Warning: this will delete all emoji associations")
@commands.check_any(commands.has_role(ROLE_NEEDED), commands.has_permissions(manage_roles=True))
async def deactivate(ctx):      # Removes the dectionary entry for this channel
    if ctx.channel in EmojiAssignments:
        EmojiAssignments.pop(ctx.channel)
        await ctx.send(f"RoleBot is no longer active in {ctx.channel.name}")

    else:
        await ctx.send(f"RoleBot was not active in {ctx.channel.name}")

@deactivate.error
async def deactivate_error(ctx, error):
    if not await general_error(ctx, error): raise

@bot.command(name="assign", help=" - Assigns an emoji to a role. Usage: `rb assign [emoji] [role name]`")
@commands.check_any(commands.has_role(ROLE_NEEDED), commands.has_permissions(manage_roles=True))
async def assign_emoji(ctx, emoji, roleString):
    if ctx.channel not in EmojiAssignments:
        await ctx.send(NOT_ACTIVE_MESSAGE.format(channel_name = ctx.channel.name))
        return
    role = discord.utils.find(lambda r: r.name == roleString, ctx.guild.roles)
    if not role:
        await ctx.send(f"{roleString} is not a valid role. Assignment of {emoji} has not changed.")
        return
    if role > ctx.guild.get_member(bot.user.id).top_role:
        await ctx.send(f"I do not have permission to assign or revoke {role.name} due to its position in the hierarchy. Assignment of {emoji} has not changed.")
        return
    PreviousRole = None
    if emoji in EmojiAssignments[ctx.channel]:
        PreviousRole = EmojiAssignments[ctx.channel][emoji]
    EmojiAssignments[ctx.channel][emoji] = role
    if PreviousRole:
        message = await ctx.send(f"Reassigned {emoji} from {PreviousRole.name} to {EmojiAssignments[ctx.channel][emoji].name}")
    else:
        message = await ctx.send(f"{emoji} asssigned to {EmojiAssignments[ctx.channel][emoji].name}")
    try:
        await message.add_reaction(emoji)
    except discord.errors.HTTPException:
        await message.delete()
        EmojiAssignments[ctx.channel].pop(emoji)
        await ctx.send(f"Something went wrong. Are you sure \"{emoji}\" is an emoji? \"{emoji}\" is not assigned.")
        return
    except:
        raise

@assign_emoji.error
async def assign_error(ctx, error):
    if not await general_error(ctx, error): raise


@bot.command(name="deassign", help=" - Removes the association from an emoji to a role. Usage: `rb deassign [emoji]`")
@commands.check_any(commands.has_role(ROLE_NEEDED), commands.has_permissions(manage_roles=True))
async def deassign_emoji(ctx, emoji):
    if ctx.channel not in EmojiAssignments:
        await ctx.send(NOT_ACTIVE_MESSAGE.format(channel_name = ctx.channel.name))
        return
    PreviousRole = None
    if emoji in EmojiAssignments[ctx.channel]:
        PreviousRole = EmojiAssignments[ctx.channel][emoji]
        EmojiAssignments[ctx.channel].pop(emoji)
    if PreviousRole:
        await ctx.send(f"{emoji} is no longer assigned to {PreviousRole.name}")
    else:
        await ctx.send(f"{emoji} was not assigned")

@deassign_emoji.error
async def deassign_error(ctx, error):
    if not await general_error(ctx, error): raise

@bot.event
async def on_reaction_add(reaction, user):
    cnl = reaction.message.channel
    if (cnl not in EmojiAssignments) or (reaction.message.author != bot.user) or (str(reaction.emoji) not in EmojiAssignments[cnl]) or (user == bot.user):
        return
    try:
        await user.add_roles(EmojiAssignments[cnl][str(reaction.emoji)], reason="RoleBot")
    except discord.Forbidden:
        await cnl.send(f"I do not have sufficient permissions to assign {EmojiAssignments[cnl][str(reaction.emoji)].name}")
    except:
        raise
    else:
        print(f"{user.name} given role {EmojiAssignments[cnl][str(reaction.emoji)].name}")

@bot.event
async def on_reaction_remove(reaction, user):
    cnl = reaction.message.channel
    if (cnl not in EmojiAssignments) or (reaction.message.author != bot.user) or (str(reaction.emoji) not in EmojiAssignments[cnl]) or (user == bot.user):
        return
    if EmojiAssignments[cnl][str(reaction.emoji)] not in user.roles:
        print(f"{user.name} did not have role {EmojiAssignments[cnl][str(reaction.emoji)].name}")
        return
    try:
        await user.remove_roles(EmojiAssignments[cnl][str(reaction.emoji)], reason="RoleBot")
    except discord.Forbidden:
        await cnl.send(f"I do not have sufficient permissions to revoke {EmojiAssignments[cnl][str(reaction.emoji)].name}")
    except:
        raise
    else:
        print(f"{user.name} lost role {EmojiAssignments[cnl][str(reaction.emoji)].name}")

@bot.command(name="save", help=" - Saves the (channel, emoji)->role dict into a json file")
@commands.check_any(commands.has_role(ROLE_NEEDED), commands.has_permissions(manage_roles=True))
async def save_command(ctx):
    if save():
        await ctx.send("Error saving file")
    else:
        await ctx.send(f"File saved as {SAVE_FILE}")
        print("File saved")

@save_command.error
async def save_error(ctx, error):
    if not await general_error(ctx, error): raise

@bot.command(name="send", help=" - Saves the (channel, emoji)->role dict into a json file and then sends to the channel in which this was run")
@commands.check_any(commands.has_role(ROLE_NEEDED), commands.has_permissions(manage_roles=True))
async def send_command(ctx):
    if save():
        await ctx.send("Error saving file")
    else:
        try:
            with open(SAVE_FILE) as f:
                await ctx.send(f"File saved as {SAVE_FILE}", file=discord.File(f, SAVE_FILE))
        except:
            raise
            await ctx.send("File saved, but could not be sent")
        else:
            print("File saved and sent")

@send_command.error
async def send_error(ctx, error):
    if not await general_error(ctx, error): raise

async def general_error(ctx, error):
    InChannel = (ctx.channel in EmojiAssignments)
    if not InChannel: await ctx.send(NOT_ACTIVE_MESSAGE.format(channel_name = ctx.channel.name))
    if isinstance(error, commands.CheckFailure):
        await ctx.send(f"You need the manage roles permission or the {ROLE_NEEDED} role to use that command")
        return True
    elif isinstance(error, commands.MissingRequiredArgument):
        if InChannel: await ctx.send(f"That is improper usage of the command")
        return True
    else:
        return False

def save():
    SavableAssignments = {}

    for cnl in EmojiAssignments:
        SavableAssignments[cnl.id] = {}
        for emoji in EmojiAssignments[cnl]:
            SavableAssignments[cnl.id][emoji] = EmojiAssignments[cnl][emoji].id

    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(SavableAssignments, f)
    except:
        return True
    else:
        return False

bot.run(TOKEN)
