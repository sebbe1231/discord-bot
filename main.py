import importlib
from os import environ
from requests import Session
from sqlalchemy.orm import Session
from database import GuildData, User, Warning, engine

import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.guilds = True
intents.members = True
intents.reactions = True
intents.dm_messages = True

def get_prefix(bot, ctx:commands.Context):
    with Session(engine) as session:
        prefix = session.query(GuildData).filter(GuildData.guild_id == ctx.guild.id).first().bot_prefix

    return prefix

bot = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=None)

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
    "twitter",
    "settings",
    "startup"
]

loaded = []
for cog in cogs:
    importlib.import_module(f'cogs.{cog}').setup(bot)
    loaded.append(cog)

print("Loaded: "+", ".join(loaded)[::-1].replace(",", " and"[::-1], 1)[::-1])

bot.run(environ['DISCORD_TOKEN'])
