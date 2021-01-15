import time
import random
import json

import discord
import discord.ext.commands

import zarya_discord


# Add links:
# Send Messages; Attach Files:
# https://discord.com/api/oauth2/authorize?client_id=799634237355065395&permissions=34816&scope=bot
# Administrator:
# https://discord.com/api/oauth2/authorize?client_id=799634237355065395&permissions=8&scope=bot


with open('settings.json', 'r') as settings_json:
    settings = json.load(settings_json)


async def discord_stutter(text, channel, delay=lambda: random.randint(1, 3)/100, skip=False):
    """Send a message to a discord channel, with gradual print effect.

    Args:
        text -- the message to send
        channel -- discord channel object to send it to
        delay -- a function that returns the time in seconds to wait between each character
        skip -- if True, message will be sent all at once instead of with the gradual effect
    """
    if skip:
        await channel.send(text)
    else:
        message = await channel.send(text[0])
        for i in range(1, len(text)):
            await message.edit(text[:i])
            time.sleep(delay())


def input_from_message(message, channel, prefixes=None):
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
        prefixes = ['>', '9v']

    if not channel or message.channel.name == channel:
        for prefix in prefixes:
            if message.content.startswith(prefix):
                return message.content.removeprefix(prefix).strip()

    return ''


async def discord_input(client, channel, prefixes=None):
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
        new_message = await client.wait_for('message')
        check = input_from_message(new_message, channel, prefixes)
        if check:
            return check


async def send_logs(channel, path='log.txt'):
    """Send logs to a discord channel."""
    await channel.send(file=discord.File(path))


client = discord.ext.commands.bot.Bot(command_prefix=('>', '9v'))


@client.command(aliases=['log', 'log.txt'])
async def logs(ctx):
    await send_logs(ctx.channel)


@client.command()
async def play(ctx):
    zarya_discord.log_start()
    await zarya_discord.run_game(client, ctx.channel)


if __name__ == '__main__':
    client.run(settings['discord']['token'])
