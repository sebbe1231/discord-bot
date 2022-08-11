import asyncio
import random
from helpers import db

import discord
from discord.ext import commands
from database import UserRelations, engine


class Gamble(commands.Cog):
    """Commands for your gambling needs (STILL IN THE WORKS, im lazy)"""
    def __init__(self, bot):
        self.bot = bot
        self.emoji = ":game_die:"

    @commands.command(aliases=["dd"])
    async def ddice(self, ctx: commands.Context, guess: int, bet: int):
        """Role a dice with 6 faces"""
        result = random.randint(1, 6)
        
        embed = discord.Embed(title=":game_die: Rolling...",
                              color=discord.Color.purple())
        msg = await ctx.reply(embed=embed)
        await asyncio.sleep(random.randint(1, 3))
        color = discord.Color.red()
        if result == guess:
            color = discord.Color.green()
            
        embed_result = discord.Embed(title=":game_die: The dice landed!",
                                     description=f"The dice landed on **{result}**", color=color)
        
        await msg.edit(embed=embed_result)

    @commands.command(aliases=["d"])
    async def dice(self, ctx: commands.Context, bet=None, guess=None):
        """Role a 6 faced dice, and try your luck (3x multiplier)"""
        money = int(20)

        if bet is None or guess is None:
            return await ctx.reply("Give me bet amount and guess \n ``.help dice``")

        # check if value is int, if not, reply saying they are noob
        try:
            bet = int(bet)
            guess = int(guess)
            if guess > 6 or guess < 1:
                await ctx.reply("Your guess is not between 1 and 6, like normal dice...")
                return
            if bet < 1:
                await ctx.reply("Your bet is too low")
                return
        except ValueError:
            return await ctx.reply("Give me bet amount and guess \n ``.help dice``")

        if bet > money:
            await ctx.reply("No money L")
            return

        # setting up embed
        embed = discord.Embed(title=":game_die: Rolling...",
                              color=discord.Color.dark_grey())
        embed.add_field(name="Your bet:", value=bet, inline=True)
        embed.add_field(name="Your guess:", value=guess, inline=True)

        msg = await ctx.reply(embed=embed)

        # wait 1-3 seconds, then reply with answer
        die_result = random.randint(1, 6)
        result_disc = "You lost :("
        result_color = discord.Color.red()
        money = money-bet
        change = f"-{bet}"
        if guess == die_result:
            result_disc = "You Won!"
            result_color = discord.Color.green()
            money = money+(3*bet)
            change = f"+{bet}"

        embed_result = discord.Embed(
            title=":game_die: Results are in!", description=result_disc, color=result_color)
        embed_result.add_field(name="Dice landed on:",
                               value=die_result, inline=False)
        embed_result.add_field(name="Your bet:", value=bet, inline=True)
        embed_result.add_field(name="Your guess:", value=guess, inline=True)
        embed_result.add_field(name="Current Money:",
                               value=money, inline=False)
        embed_result.add_field(name="Change:", value=change, inline=True)

        # needs to be 3x points
        await asyncio.sleep(random.randint(1, 3))
        await msg.edit(embed=embed_result)

    @commands.command()
    async def losemoney(self, ctx: commands.Context):
        await ctx.send(ctx.author.id)
        relation = db.get_user_relation(ctx.author.id, ctx.guild.id)

    @commands.command()
    async def coinflip(self, ctx: commands.Context):
        """Flip a coin, garenteed 50% chance (Still in the works)"""
        pass


def setup(bot: commands.Bot):
    bot.add_cog(Gamble(bot))
