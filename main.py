import discord
from discord.ext import commands
import os

import config
import logging
from datetime import datetime

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix = commands.when_mentioned_or(config.prefix),
    allowed_mentions = discord.AllowedMentions(everyone = False),
    case_insensitive = True,
    activity = discord.Activity(type = discord.ActivityType.watching, name = ";help"),
    intents = intents
)

bot.remove_command('help')
bot.load_extension("jishaku")

bot.start_time = datetime.utcnow()


logging.basicConfig(level=logging.INFO)


@bot.event
async def on_ready():
    print(f"Loaded on {len(bot.guilds)} guilds")


cogs = os.listdir('./cogs')
utils = os.listdir('./utils')

for x, y in [(cogs, utils)]:
    for cog_file in cogs:
        if cog_file.endswith('.py'):
            try:
                bot.load_extension(f'cogs.{cog_file[:-3]}')
            except Exception as e:
                raise e
    for utils_file in utils:
        if utils_file.endswith('.py'):
            try:
                bot.load_extension(f'utils.{utils_file[:-3]}')
            except Exception as e:
                raise e

bot.run(config.token)
