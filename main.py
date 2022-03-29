import importlib
import random
from os import environ

import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.presences = True
intents.members = True

prefix = "."
bot = commands.Bot(prefix, intents=intents, help_command=None)


@bot.event
async def on_ready():
    print("Bot is ready!")

cogs = [
    "admin",
    "gamble",
    "funny",
    "profile",
    "detection",
    "error",
    "reddit",
    "help",
    "twitter"
]

loaded = []
for cog in cogs:
    importlib.import_module(f'cogs.{cog}').setup(bot)
    loaded.append(cog)

print("Loaded: "+", ".join(loaded)[::-1].replace(",", " and"[::-1], 1)[::-1])

bot.run(environ['DISCORD_TOKEN'])
