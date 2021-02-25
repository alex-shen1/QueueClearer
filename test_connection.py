"""
Excerpt from main.py with only the part testing if the bot is connected.
"""
import os
import discord
from dotenv import load_dotenv

load_dotenv()

# Discord API token. Links to the bot account, needed in env to work.
""" Discord API token. Links to the bot account, needed in env to work."""
TOKEN = os.getenv('DISCORD_TOKEN')

""" Discord client object. Needs to run at the end and be declared before these decorators, idk."""
client = discord.Client()


@client.event
async def on_ready():
    """Simply prints out a message to confirm the bot is connected."""
    print(f'{client.user} is connected to the following servers:')
    for guild in client.guilds:
        print(f'{guild.name}(id: {guild.id})')


client.run(TOKEN)
