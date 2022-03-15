import asyncio
from multiprocessing.sharedctypes import Value
from turtle import color, title
from unittest import result
import discord
from discord.ext import commands
import random


class Gamble(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ddice(self, ctx: commands.Context, arg1 = None):
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
    
    @commands.command()
    async def dice(self, ctx: commands.Context, bet = None, guess = None):
        if bet is None or guess is None:
            await ctx.reply("Give me bet amount and guess \n .dice [bet] [guess]")
        
        #check if value is int, if not, reply saying they are noob
        try:
            bet = int(bet)
            guess = int(guess)
            if guess > 6 or guess <1:
                await ctx.reply("Your guess is not between 1 and 6, like normal dice...")
                return
            if bet < 1:
                await ctx.reply("Your bet is too low")
                return
        except ValueError:
            await ctx.reply("Give me bet amount and guess \n .dice [bet] [guess]")
            return
        
        #setting up embed
        embed = discord.Embed(title = ":game_die: Rolling...", color=discord.Color.dark_grey())
        embed.add_field(name="Your bet:", value=bet, inline=True)
        embed.add_field(name="Your guess:", value=guess, inline=True)

        msg = await ctx.reply(embed=embed)

        #wait 1-3 seconds, then reply with answer
        die_result = random.randint(1, 6)
        result_disc = "You lost :("
        result_color = discord.Color.red()
        if guess == die_result:
            result_disc = "You Won!"
            result_color = discord.Color.green()

        embed_result = discord.Embed(title = ":game_die: Results are in!", description = result_disc, color=result_color)
        embed_result.add_field(name="Dice landed on:", value=die_result, inline=False)
        embed_result.add_field(name="Your bet:", value=bet, inline=True)
        embed_result.add_field(name="Your guess:", value=guess, inline=True)
        
        #needs to be 3x points
        await asyncio.sleep(random.randint(1, 3))
        await msg.edit(embed = embed_result)

    @commands.command()
    async def coinflip(self, ctx: commands.Context):
        pass
        
        

def setup(bot: commands.Bot):
    bot.add_cog(Gamble(bot))
