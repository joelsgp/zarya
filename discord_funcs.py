import time
import random
import json

import discord
import discord.ext.commands

import zarya_discord


# TODO: improved framework, compatibility with builtin print and input, more features, etc.
# TODO: create strings file, csv parser for translations, lang setting in settings
# TODO: add func to change persistent settings


# Add links:
# Send Messages; Attach Files:
# https://discord.com/api/oauth2/authorize?client_id=799634237355065395&permissions=34816&scope=bot
# Administrator:
# https://discord.com/api/oauth2/authorize?client_id=799634237355065395&permissions=8&scope=bot


PREFIXES = (
    '>', '> ',
    '9v', '9v ',
)


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
    if not text:
        return

    if skip:
        await channel.send(text)
    else:
        # part_len = len(text) // 5
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


async def send_logs(channel, path='log.txt'):
    """Send logs to a discord channel."""
    await channel.send(file=discord.File(path))


help_command = discord.ext.commands.DefaultHelpCommand(no_category="Commands (prefixes - '>', '9v')")


client = discord.ext.commands.bot.Bot(command_prefix=PREFIXES, help_command=help_command)


@client.event
async def on_ready():
    print('Bot running.')


@client.command(aliases=['log', 'log.txt'])
async def logs(ctx):
    await send_logs(ctx.channel)


@client.command()
async def play(ctx):
    zarya_discord.log_start()
    # await zarya_discord.run_game(client, ctx.channel, settings['discord']['channel'])
    await zarya_discord.run_game(client, ctx.channel, ctx.channel.name)


if __name__ == '__main__':
    client.run(settings['discord']['token'])
