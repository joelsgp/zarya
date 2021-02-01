import time
import random


# TODO: improved framework, compatibility with builtin print and input, more features, etc.
# TODO: create strings file, csv parser for translations, lang setting in settings
# TODO: add func to change persistent settings

DISCORD_MESSAGE_LEN_LIMIT = 2000
PREFIXES = (
    '>', '> ',
    '9v', '9v ',
)


async def discord_stutter(text, channel, delay=lambda: random.randint(1, 3)/100, skip=False):
    """Send a message to a discord channel, with gradual print effect.

    Args:
        text -- the message to send
        channel -- discord channel object to send it to
        delay -- a function that returns the time in seconds to wait between each character
        skip -- if True, message will be sent all at once instead of with the gradual effect
    """
    if not text:
        return

    # recurse to send the message in parts if it's over the message length limits
    if len(text) > DISCORD_MESSAGE_LEN_LIMIT:
        part_len = DISCORD_MESSAGE_LEN_LIMIT
        parts = [text[i:i + part_len] for i in range(0, len(text), part_len)]
        for part in parts:
            await discord_stutter(part, channel, delay, skip)
        return

    if skip:
        await channel.send(text)
    else:
        if len(text) > 500:
            part_len = len(text) // 5
        else:
            part_len = 100
        parts = [text[i:i+part_len] for i in range(0, len(text), part_len)]

        message = await channel.send(parts[0])
        for i in range(2, len(parts)+1):
            await message.edit(content=''.join(parts[:i]))
            time.sleep(delay())


def input_from_message(message, req_channel_name, prefixes=None):
    """Get input from a discord message.

    Args:
        message -- discord message object
        channel -- discord channel to pay attention to messages in, all channels if this is False
        prefixes -- list of command prefixes
    Returns:
        The message with the prefix removed. The return value will be an empty string if conditions were not met,
        which means this function can be used to check validity and to strip prefixes.
    """
    if not prefixes:
        prefixes = PREFIXES

    if not req_channel_name or message.channel.name == req_channel_name:
        for prefix in prefixes:
            if message.content.startswith(prefix):
                return message.content.removeprefix(prefix).strip()

    return ''


async def discord_input(discord_client, req_channel_name, prefixes=None):
    """Wait for a discord message with valid input, then return it.

    Like the builtin input() function but for discord
    Args:
        client -- discord client object
        channel -- discord channel to pay attention to messages in
        prefixes -- list of command prefixes
    Returns:
        String content from a valid message, with the prefix removed.
    """
    while True:
        new_message = await discord_client.wait_for('message')
        check = input_from_message(new_message, req_channel_name, prefixes)
        if check:
            return check
