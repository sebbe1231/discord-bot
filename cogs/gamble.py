import asyncio
from turtle import title
import discord
from discord.ext import commands
import random


class Gamble(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def dice(self, ctx: commands.Context, arg1 = None):
        if arg1 is None:
            arg1 = 6

        try:
            result = random.randint(1, int(arg1))
        except ValueError:
            await ctx.reply("say a number >:(")

        embed = discord.Embed(title=":game_die: Rolling...",
                              color=discord.Color.purple())
        msg = await ctx.reply(embed=embed)
        await asyncio.sleep(random.randint(1,3))
        embed_result = discord.Embed(title = ":game_die: you got!:", 
                                     description = result, color=discord.Color.purple())
        await msg.edit(embed = embed_result)
        

def setup(bot: commands.Bot):
    bot.add_cog(Gamble(bot))
