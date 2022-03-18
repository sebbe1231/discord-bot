import asyncio
import random

import discord
from discord.ext import commands


class Gamble(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["dd"])
    async def ddice(self, ctx: commands.Context, NumDice=None):
        if NumDice is None:
            NumDice = 6

        try:
            result = random.randint(1, int(NumDice))
        except ValueError:
            await ctx.reply("say a number >:(")

        embed = discord.Embed(title=":game_die: Rolling...",
                              color=discord.Color.purple())
        msg = await ctx.reply(embed=embed)
        await asyncio.sleep(random.randint(1, 3))
        embed_result = discord.Embed(title=":game_die: you got!:",
                                     description=result, color=discord.Color.purple())
        await msg.edit(embed=embed_result)

    @commands.command(aliases=["d"])
    async def dice(self, ctx: commands.Context, bet=None, guess=None):
        money = int(20)

        if bet is None or guess is None:
            return await ctx.reply("Give me bet amount and guess \n .dice [bet] [guess]")

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
            return await ctx.reply("Give me bet amount and guess \n .dice [bet] [guess]")

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
    async def coinflip(self, ctx: commands.Context):
        pass


def setup(bot: commands.Bot):
    bot.add_cog(Gamble(bot))
