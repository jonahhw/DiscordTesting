# Role Bot for Discord
Assigns roles based on reactions to messages

## Command list
Default prefix is "rb "
* list: lists all of the emoji-role bindings for the channel in which it's run, and reacts with all of those emoji

*Commands below this require a specific role or manage roles permission to use*
* activate: activates in the channel in which it's run
* deactivate: deactivates in the channel in which it's run
* assign: assigns the emoji to a role. Usage: `rb assign [emoji] [role_name]`
* deassign: deassigns the emoji from any roles. Usage: `rb deassign [emoji]`
* save: saves the current list of channel/emoji->role assignments as a json file which will be automatically loaded on the next startup
* send: saves the file just like `rb save` and then sends it to the chat

*Commands below this require a(n optionally different) specific role or can be disabled in bot.py*
* load: loads the last saved state (when save or send was last run)
* clear: clears all channel/emoji->role assignments

## Install
1. Create a Discord bot and copy its bot token (look up a tutorial if you don't know how)
1. Scroll down to "Privileged Gateway Intents" and enable "Server Members Intent". (This is necessary for detecting when reactions are removed.)
1. Make sure that you have python and pip installed
1. Install all dependencies in requirements.txt (just discord.py at the time of writing)
    * Run `pip install -r requirements.txt` to do this in one command
1. Ceate a file called env.py in the same directory as bot.py. It should contain:
```python
# env.py
DISCORD_TOKEN = "[your bot token here]"
```
1. Edit what you want to at the top of "bot.py", including prefix, roles needed, and the save file name
1. Run with `python bot.py`

I've designed this so that it should work with more than one server connected, but I haven't tested it. Any command that involves clearing, saving, or loading the assignments will affect all servers. It also is not super robust with missing permissions yet so it will probably throw errors if it doesn't have permissions it expects to have. In general, it's best suited to a small server with people you trust.

## How it works
The main way this program operates is using a nested dictionary. The fist key is the channel it's operating in, the second key is the emoji (stored as a string), and the output is the role that will be assigned when that emoji is reacted in that channel. When it recieves a reaction, it simply follows the dictionary and assigns the role it finds. To save the dictionary, it has a somewhat roundabout process. Since things like pickle (and even dill) don't work on discord.py types such as channels and roles, I made it get their IDs then save them into a json file that way. Then, when it goes to read them again, it first searches through all the channels of all the guilds it's connected to and assigns a channel based on the channel id, then looks through all the roles on that server for matching IDs.

