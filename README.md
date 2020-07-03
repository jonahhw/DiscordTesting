# Role Bot for Discord
Assigns roles based on reactions to messages

## Install
1. Create a Discord bot and copy its bot token (look up a tutorial if you don't know how)
1. Make sure that you have python and pip installed
1. Install all dependencies in requirements.txt (just discord.py at the time of writing)
    * Run `pip install -r requirements.txt` to do this in one command
1. Ceate a file called env.py in the same directory as bot.py. It should contain:
```python
# env.py
DISCORD_TOKEN = "[your bot token here]"
```
1. Run with `python bot.py`

## Command list
Default prefix is "rb ", which you can change in the declaration of bot at the top.
* list: lists all of the emoji-role bindings for the channel in which it's run, and reacts with all of those emoji

*Commands below this require a specific role or manage roles permission to use*
* activate: activates in the channel in which it's run
* deactivate: deactivates in the channel in which it's run
* assign: assigns the emoji to a role. Usage: `rb assign [emoji] [role_name]`
* deassign: deassigns the emoji from any roles. Usage: `rb deassign [emoji]`
* save: saves the current list of channel/emoji->role assignments as a json file which will be automatically loaded on the next startup
* send: saves the file just like `rb save` and then sends it to the chat

## How it works
The main way this program operates is using a nested dictionary. The fist key is the channel it's operating in, the second key is the emoji (stored as a string), and the output is the role that will be assigned when that emoji is reacted in that channel. When it recieves a reaction, it simply follows the dictionary and assigns the role it finds. To save the dictionary, it has a somewhat roundabout process. Since things like pickle (and even dill) don't work on discord.py types such as channels and roles, I made it first get their IDs, then save them into a json file that way. Then, when it goes to read them again, it first searches through all the channels of all the guilds it's connected to and assigns a channel based on the channel id, then looks through all the roles on that server for matching IDs. (Fortunately emoji - even custom ones - can be stored as strings.)

