#!/usr/bin/env python

import os
import json

import discord
import discord.ext.commands

import game.zarya_discord as zarya_discord


# todo: update readme

# Add links:
# Send Messages; Attach Files:
# https://discord.com/api/oauth2/authorize?client_id=799634237355065395&permissions=34816&scope=bot
# Administrator:
# https://discord.com/api/oauth2/authorize?client_id=799634237355065395&permissions=8&scope=bot


GITHUB_URL = 'https://github.com/JMcB17/Zarya'
PREFIXES = (
    '>', '> ',
    '9v', '9v ',
)

with open('settings.json', 'r') as settings_json:
    settings = json.load(settings_json)

help_command = discord.ext.commands.DefaultHelpCommand(no_category="Commands (prefixes - '>', '9v')")
client = discord.ext.commands.bot.Bot(command_prefix=PREFIXES, help_command=help_command)


@client.event
async def on_ready():
    print('Bot running.')


@client.command(aliases=['github'])
async def git(ctx):
    await ctx.channel.send(f'<{GITHUB_URL}>')


@client.command(aliases=['log', 'log.txt'])
async def logs(ctx):
    try:
        file = discord.File(os.path.join('game', 'log.txt'))
    except FileNotFoundError:
        await ctx.channel.send('No logs.')
    else:
        await ctx.channel.send(file=file)


# todo: fix the error every time an ingame command is used that isn't a bot command
@client.command()
async def play(ctx, *args):
    # only run with no args, to avoid crossover with in-game command
    if args:
        return
    # todo: make instancing better
    # game_instance = zarya_discord.ZaryaGame(client, ctx.channel, settings['discord']['channel'])
    game_instance = zarya_discord.ZaryaGame(client, ctx.channel, ctx.channel.name)
    game_instance.log_start()
    await game_instance.run()
    del game_instance


if __name__ == '__main__':
    client.run(settings['discord']['token'])
