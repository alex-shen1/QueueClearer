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

""" Name of voice channel for the OH waiting room. Defaults to value used by the CS 3240 server. """
WAITING_ROOM_CHANNEL = os.getenv('OH_QUEUE_CHANNEL', default='Office Hours Waiting Room')

""" Discord client object. Needs to run at the end and be declared before these decorators, idk."""
# Explicitly declare we need to track members (to see if old messages should be deleted)
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

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

""" Whether or not logging should be enabled."""
LOGGING = bool(os.getenv('DISCORD_TOKEN', default='False'))


@client.event
async def on_ready():
    """Simply prints out a message to confirm the bot is connected."""
    print(f'{client.user} is connected to the following servers:')
    for guild in client.guilds:
        print(f'{guild.name}(id: {guild.id})')

        # Get the queue/waiting room Channel objects - should only be 1 per server
        queue = next(channel for channel in guild.channels if channel.name == OH_QUEUE_CHANNEL)
        waiting_room = next(channel for channel in guild.channels if channel.name == WAITING_ROOM_CHANNEL)

        # Can have many different help channels (e.g. TA Room 1, TA Room 2, etc.)
        help_channels = list(filter(lambda channel: reduce(or_, map(channel.name.__contains__, INSTRUCTOR_ROOMS)),
                                    guild.channels))

        # Process all preexisting student messages upon initialization
        async for message in queue.history():
            # Need to get member instead of just using the message author because for some reason messages authors
            # that you get from queue.history() are User objects that don't have role information
            author = guild.get_member(message.author.id)
            if is_student(author):
                add_student_message(message)
                # If a student is currently in a help room, react to their message
                if reduce(or_, map(lambda channel: author in channel.members, help_channels)):
                    await message.add_reaction('👍')
                # Otherwise, if they aren't in the waiting room at all, delete their message
                elif author not in waiting_room.members:
                    await message.delete()


@client.event
async def on_message(message):
    """Adds all messages sent by students in the OH queue to `MESSAGES`."""
    if message.channel.name == OH_QUEUE_CHANNEL:
        if is_student(message.author):
            add_student_message(message)
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
                    print(member.name, 'is currently getting help!', end=' ')
                    print(f'{before.channel.name} -> {after.channel.name}' if LOGGING else '')
                    for message in MESSAGES[user_id]:
                        try:
                            await message.add_reaction('👍')
                        except discord.NotFound:
                            print(f'Message not found - seems like {member.name}\'s message was already deleted.')
            # If leaving OH entirely, then delete their messages
            else:
                print(member.name, 'has left OH, deleting their messages')
                for message in MESSAGES[user_id]:
                    try:
                        await message.delete()
                    except discord.NotFound:
                        print(f'Message not found - seems like {member.name}\'s message was already deleted.')
                MESSAGES.pop(user_id)


def add_student_message(message):
    """Given a Message object, adds it to the global MESSAGES dict."""
    user_id = message.author.id

    global MESSAGES  # Pylint doesn't like this. Too bad!
    if user_id not in MESSAGES.keys():
        print(message.author.name, 'has entered the OH queue!')
        MESSAGES[user_id] = [message]
    else:
        MESSAGES[user_id].append(message)


def is_student(user):
    """
    Checks if a user is a student and returns a boolean reflecting this.

    We need to check if user is NOT an instructor as opposed to testing
    if they are a student because there isn't a "student" role.
    """
    user_roles = set(map(str, user.roles))
    return not user_roles & INSTRUCTOR_ROLES


client.run(TOKEN)
