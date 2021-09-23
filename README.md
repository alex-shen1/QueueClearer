# QueueClearer (name subject to change)

This bot was created to manage the office hours queue for CS 3240 @ UVA. Standard practice when holding office hours is that students will send a message describing their problem into a text channel and join a waiting room voice channel while TAs work down the queue addressing issues. The issue is that the queue tends to fill up during busy times, and while TAs are supposed to delete messages to clean it up, when things get hectic this doesn't always happen. I decided there had to be a better way, so I created this bot to automate that process.

## How it works

When students come to office hours, we expect this pattern of behavior:
- Student sends message in text channel and joins queue waiting room, more or less at the same time
- TA/professor pulls student out of the waiting room into their own channel
- After receiving help, the student leaves, disconnecting from all voice channels.

Using Discord's API, the bot is capable of detecting when students send messages and move in/out of voice channels. It uses this information to more or less track student activity during office hours with this logic:
- When a student sends a message, both the message and their ID is stored. At this point, it's assumed that they are also joining the waiting room voice channel. 
- Following up on this assumption, the bot assumes that the next time the student moves between channels, they are being moved by an instructor to a help channel. At this point, the bot will put a 👍 reaction on their message(s) in the queue to signal to the other instructors that the student is being helped.
- When a student disconnects from all voice channels entirely, the bot assumes that their issue is solved and deletes their message(s) from the queue.

Critically, for the bot to work, the students cannot disconnect from any voice channel (moving between channels is fine) from the moment they enter their message, or it will be deleted.

## Deployment

The deployment of the bot used for CS 3240 will be on Heroku, just running `main.py` indefinitely. It has these config vars:
- `DISCORD_TOKEN`: Discord API token; required for the bot to work at all. The corresponding bot must also be added to the class server with the "Manage Messages" and "Add Reactions" permissions for full functionality. 
- `OH_QUEUE_CHANNEL`: The name of the text channel used for the office hours queue. Defaults to the name used by the CS 3240 server if not specified.
- `WAITING_ROOM_CHANNEL`: The name of the voice channel where students will wait for an instructor to pull them into their voice channel. Defaults to the name used by the CS 3240 server if not specified.
- `INSTRUCTOR_ROLES`: The names of roles held by instructors (professors, TAs) on the server, whose messages in the queue shouldn't be automatically deleted. Defaults to the roles used by the CS 3240 server if not specified.
- `INSTRUCTOR_ROOMS`: Some string that can be used to uniquely identify voice channels designated as "help rooms." Used to ensure that students are moving into a real office hours channel to get help before reacting to their messages. The CS 3240 server is structured that there is a "Professor Room" and "TA Room 0", "TA Room 1", etc. so the variable defaults to `'TA,Professor'` because no other channels on the server have these strings. 
- `LOGGING`: Determines whether or not (extra) logging should be enabled. Environmental variables are strings, so the variable is set to whatever calling the `bool()` constructor on the environmental value gives. Defaults to `False`. 

As of this writing (3/25/21), the bot has been in use on the official CS 3240 server for around a month now, with a generally high level of success. Performance issues have been minimal, and small bugs have been fixed as they pop up.

## Future Work
- Add commands `!openqueue` and `!closequeue` to allow more convenient opening/closing of the queue (i.e. enabling/disabling permissions to send messages in the channel). Would require additional permissions.
- Heroku recently sent me a notice that I'm almost running out of free-tier dyno hours for the month. I managed to get more just by verifying a credit card, but it'd probably be better practice to have it automatically sleep/wake at times when nobody is hosting office hours.
