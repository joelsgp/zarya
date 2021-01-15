import time
import random

import discord


# TODO: write docstrings


async def discord_stutter(text, channel, delay=lambda: random.randint(1, 3)/100, skip=False):
    if skip:
        await channel.send(text)
    else:
        message = await channel.send(text[0])
        for i in range(1, len(text)):
            await message.edit(text[:i])
            time.sleep(delay())


def input_from_message(message, channel, prefixes=None):
    if not prefixes:
        prefixes = ['>', '9v']

    if not channel or message.channel == channel:
        for prefix in prefixes:
            if message.content.startswith(prefix):
                return message.content.removeprefix(prefix).strip()

    return ''


async def discord_input(client, channel, prefixes=None):
    while True:
        new_message = await client.wait_for('message')
        check = input_from_message(new_message, channel, prefixes)
        if check:
            return check


def send_logs(channel, path='log.txt'):
    channel.send(discord.File(path))
