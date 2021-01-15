import time
import random

import discord


def input_from_message(message, prefixes):
    for prefix in prefixes:
        if message.content.startswith(prefix):
            return message.content.removeprefix(prefix).strip()

    return ''


async def stutter(text, channel, delay=lambda: random.randint(1, 3)/100, skip=False):
    if skip:
        await channel.send(text)
    else:
        message = await channel.send(text[0])
        for i in range(1, len(text)):
            await message.edit(text[:i])
            time.sleep(delay())
