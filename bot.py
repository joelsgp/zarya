#!/usr/bin/env python
import logging
import os
import subprocess
import sys
import tomllib
from typing import Optional

import discord
import discord.ext.commands

import game.zarya_discord as zarya_discord

# todo: update readme

# Add links:
# Send Messages; Attach Files:
# https://discord.com/api/oauth2/authorize?client_id=799634237355065395&permissions=34816&scope=bot
# Administrator:
# https://discord.com/api/oauth2/authorize?client_id=799634237355065395&permissions=8&scope=bot


__version__ = "0.2.0"


BOT_ADD_LINK = "https://discord.com/api/oauth2/authorize?client_id=799634237355065395&permissions=34816&scope=bot"
GITHUB_URL = "https://github.com/joelsgp/zarya"
PREFIXES = (
    ">",
    "> ",
    "9v",
    "9v ",
)

with open("config.toml", "rb") as settings_file:
    settings = tomllib.load(settings_file)


def game_instance_running_check(ctx):
    return ctx.channel.id not in ctx.bot.game_instances


help_command = discord.ext.commands.DefaultHelpCommand(
    no_category="Commands (prefixes - '>', '9v')"
)
help_command.add_check(game_instance_running_check)
intents = discord.Intents.default()
intents.message_content = True
bot = discord.ext.commands.bot.Bot(
    command_prefix=PREFIXES, help_command=help_command, intents=intents
)

bot.game_instances = {}


@bot.event
async def on_ready():
    print("Bot running.")


@bot.command(hidden=True, aliases=["update"])
@discord.ext.commands.is_owner()
async def pull(ctx, branch: Optional[str]):
    if branch:
        await ctx.send(subprocess.getoutput(f"git checkout {branch}"))
    await ctx.send(subprocess.getoutput("git pull"))


@bot.command(hidden=True)
@discord.ext.commands.is_owner()
async def restart(ctx):
    await ctx.send("Restarting bot.")
    # pm2 should start it again
    sys.exit()


@bot.command(aliases=["inv", "add"], description="Get the bot add link")
async def invite(ctx):
    await ctx.send(f"<BOT_ADD_LINK>")


@bot.command(
    name="github-link",
    aliases=["github", "git"],
    description="Get the bot source code link",
)
async def github_link(ctx):
    await ctx.send(f"<{GITHUB_URL}>")


@bot.command(aliases=["log", "log.txt"])
async def logs(ctx):
    try:
        file = discord.File(os.path.join("game", "log.txt"))
    except FileNotFoundError:
        await ctx.send("No logs.")
    else:
        await ctx.send(file=file)


# todo: fix the error every time an ingame command is used that isn't a bot command
@bot.command()
async def play(ctx):
    if ctx.channel.id in bot.game_instances:
        return

    game_instance = zarya_discord.ZaryaGame(bot, ctx.channel, ctx.channel.name)
    bot.game_instances[ctx.channel.id] = game_instance

    game_instance.log_start()
    # todo: catch errors better (might fail to close the instance if it errors)
    await game_instance.run()

    bot.game_instances.pop(ctx.channel.id)


def main():
    formatter = logging.Formatter(logging.BASIC_FORMAT)
    print("Bot starting..")
    bot.run(settings["discord"]["token"], log_formatter=formatter)


if __name__ == "__main__":
    main()
