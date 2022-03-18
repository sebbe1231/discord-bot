from datetime import datetime
from random import choice

import asyncpraw
import asyncprawcore.exceptions as prawexceptions
import discord
from discord.ext import commands
from os import environ


class Reddit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.reddit = asyncpraw.Reddit(
            client_id=environ['PRAW_CLIENT_ID'],
            client_secret=environ['PRAW_CLIENT_SECRET'],
            user_agent=environ['PRAW_USER_AGENT']
        )

        print(f"reddit sat up? {self.reddit.read_only}")

    @commands.command(aliases=["reddit"])
    async def subreddit(self, ctx: commands.Context, subreddit):
        if subreddit is None:
            return await ctx.reply("Give me a subreddit")

        # loading embed
        loading_embed = discord.Embed(
            title="Loading...", description=f"Submitted by @{ctx.author}")
        msg = await ctx.reply(embed=loading_embed)

        try:
            # getting values
            subreddit = await self.reddit.subreddit(subreddit)

            submissions = [subm async for subm in subreddit.hot(limit=100)]
            submission = choice(submissions)
        except (prawexceptions.Redirect, prawexceptions.Forbidden):
            await ctx.reply("This subreddit does not exist, or is currently not accessible")
            return await msg.delete()

        if submission.over_18:
            if ctx.channel.is_nsfw():
                pass
            else:
                await ctx.reply("NSFW is only allowed in NSFW channels")
                return await msg.delete()

        # create answer embed
        finished_embed = discord.Embed(
            title=f"r/{submission.subreddit}", url=f"https://reddit.com{submission.permalink}")
        if submission.is_self:
            try:
                finished_embed.add_field(
                    name=submission.title, value=str(submission.selftext))
            except commands.CommandInvokeError:
                return ctx.reply("Post too big")
        else:
            finished_embed.add_field(name=submission.title, value="** **")
            finished_embed.set_image(url=submission.url)

        finished_embed.set_author(
            name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        finished_embed.set_footer(
            text=f"upvotes: {submission.score} \nreddit.com/u/{submission.author} \nuploaded: {datetime.utcfromtimestamp(submission.created_utc).strftime('%Y-%m-%d')}")

        try:
            await msg.edit(embed=finished_embed)
        except commands.CommandInvokeError:
            return await ctx.reply("Post too big")


def setup(bot: commands.Bot):
    bot.add_cog(Reddit(bot))
