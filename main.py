import importlib
import random
from secret import DISCORD_TOKEN

import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.presences = True
intents.members = True

bot = commands.Bot(".", intents=intents)

@bot.event
async def on_ready():
    print("Bot is ready!")

cogs = [
    "admin",
    "gamble",
    "funny",
    "profile",
    "detection"
]

for cog in cogs:
    importlib.import_module(f'cogs.{cog}').setup(bot)

    print(f"Loaded: {cog}")

bot.run(DISCORD_TOKEN)
