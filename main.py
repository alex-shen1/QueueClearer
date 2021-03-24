"""
Code for my office hours helping bot.
"""
import os
import discord
from dotenv import load_dotenv
from functools import reduce
from operator import or_

# pylint:disable=fixme,global-statement

load_dotenv()

# Discord API token. Links to the bot account, needed in env to work.
""" Discord API token. Links to the bot account, needed in env to work."""
TOKEN = os.getenv('DISCORD_TOKEN')

""" Name of channel for office hours queue. Defaults to value used by the CS 3240 server."""
OH_QUEUE_CHANNEL = os.getenv('OH_QUEUE_CHANNEL', default='office-hours-queue')

""" Discord client object. Needs to run at the end and be declared before these decorators, idk."""
client = discord.Client()

""" Dictionary mapping student Discord IDs to a list of Message objects they have sent in OH queue."""
MESSAGES = {}

""" Set of roles held by staff, whose messages we DON'T want automatically deleted from the queue.
    Defaults to values used by the CS 3240 server."""
INSTRUCTOR_ROLES = set(os.getenv('INSTRUCTOR_ROLES', default='teaching-assistant,professor')
                       .split(','))

""" Set of unique strings that are contained in the names of instructor rooms (e.g. TA Room 1, etc.)
    Defaults to values used by the CS 3240 server."""
INSTRUCTOR_ROOMS = set(os.getenv('INSTRUCTOR_ROOMS', default='TA,Professor')
                       .split(','))


@client.event
async def on_ready():
    """Simply prints out a message to confirm the bot is connected."""
    print(f'{client.user} is connected to the following servers:')
    for guild in client.guilds:
        print(f'{guild.name}(id: {guild.id})')


@client.event
async def on_message(message):
    """Adds all messages sent by students in the OH queue to `MESSAGES`."""
    if message.channel.name == OH_QUEUE_CHANNEL:
        if is_student(message.author):
            user_id = message.author.id

            global MESSAGES  # Pylint doesn't like this. Too bad!
            if user_id not in MESSAGES.keys():
                print(message.author.name, 'has entered the OH queue!')
                MESSAGES[user_id] = [message]
            else:
                MESSAGES[user_id].append(message)
        else:
            print(f'Instructor {message.author.nick}: {message.content}')


@client.event
async def on_voice_state_update(member, before, after):
    """
    Logic in response to a given user switching between channels.

    Technically triggers when any user on the server changes their
    "voice state" which can mean a bunch of different things, but the one
    we care about is channel membership. Even more technically, we only
    care about when students leave OH queue/a help room, which we implement
    by checking against the stored messages.
    """
    user_id = member.id
    # If user is in the messages, they must have sent a msg in OH queue
    if user_id in MESSAGES.keys():
        # User must be leaving a voice channel, either OH queue or help room
        if before.channel is not None:
            # If they're moving into a channel for help, thumbs up react their messages
            if after.channel is not None:
                # Make sure the room they're joining is actually an instructor room
                if reduce(or_, map(after.channel.name.__contains__, INSTRUCTOR_ROOMS)):
                    print(member.name, 'is currently getting help!')
                    for message in MESSAGES[user_id]:
                        await message.add_reaction('👍')
            # If leaving OH entirely, then delete their messages
            else:
                print(member.name, 'has left OH, deleting their messages')
                for message in MESSAGES[user_id]:
                    await message.delete()
                    MESSAGES.pop(user_id)


def is_student(user):
    """
    Checks if a user is a student and returns a boolean reflecting this.

    We need to check if user is NOT an instructor as opposed to testing
    if they are a student because there isn't a "student" role.
    """
    user_roles = set(map(str, user.roles))
    return not user_roles & INSTRUCTOR_ROLES


client.run(TOKEN)
