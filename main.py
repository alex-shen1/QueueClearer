import os
import discord

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = 'spArk\'s server'
intents = discord.Intents.all()
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )


@client.event
async def on_typing(channel, user, when):
    print(channel, user, when)


client.run(TOKEN)
