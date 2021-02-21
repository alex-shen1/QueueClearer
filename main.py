import os
import discord

from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = 'spArk\'s server'


# @client.event
# async def on_ready():
#     for guild in client.guilds:
#         if guild.name == GUILD:
#             break
#
#     print(
#         f'{client.user} is connected to the following guild:\n'
#         f'{guild.name}(id: {guild.id})'
#     )

class NewClient(discord.Client):
    async def on_ready(self):
        for guild in client.guilds:
            if guild.name == GUILD:
                break
        print(self.users)
        print(
            f'{client.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})'
        )

client = NewClient()
client.run(TOKEN)