import os
import discord

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = 'alex\'s test server for fun dev times'
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

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
    print(user, "is typing in", channel)


messages = {}


@client.event
async def on_message(message):
    print(message)

    if message.channel.name == 'office-hours-queue':
        print("this was in the queue!")
        user_id = message.author.id

        global messages
        if user_id not in messages.keys():
            messages[user_id] = [message]
        else:
            messages[user_id].append(message)
        show_messages(user_id)


@client.event
async def on_voice_state_update(member, before, after):
    print(member, before, after)
    # print(messages)
    if before.channel is not None and after.channel is None:
        user_id = member.id
        if user_id in messages.keys():
            for message in messages[user_id]:
                await message.delete()
            messages.pop(user_id)
    # print(before.channel.name, after.channel.name)


def show_messages(user_id):
    for message in messages[user_id]:
        print(message.content)
        pass


client.run(TOKEN)
