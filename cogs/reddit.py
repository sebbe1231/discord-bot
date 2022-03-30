from datetime import datetime
from random import choice
import random

import asyncpraw
import asyncprawcore.exceptions as prawexceptions
import discord
from discord.ext import commands
from os import environ


class Reddit(commands.Cog):
    """Commands utilizing the reddit API"""
    def __init__(self, bot):
        self.bot = bot
        self.emoji = ":poop:"

        self.reddit = asyncpraw.Reddit(
            client_id=environ['PRAW_CLIENT_ID'],
            client_secret=environ['PRAW_CLIENT_SECRET'],
            user_agent=environ['PRAW_USER_AGENT']
        )

        print(f"reddit sat up? {self.reddit.read_only}")

    @commands.command(aliases=["reddit"])
    async def subreddit(self, ctx: commands.Context, subreddit):
        """Picks a random post from your chosen subreddit (some subreddits will not load, i cant explain why... cause idk)"""
        if subreddit is None:
            return await ctx.reply("Give me a subreddit")

        # loading embed
        loading_embed = discord.Embed(
            title="Loading...", description=f"Submitted by @{ctx.author}")
        msg = await ctx.reply(embed=loading_embed)

        error_embed = discord.Embed(title="ERROR", color=discord.Color.red())

        try:
            # getting values
            subreddit = await self.reddit.subreddit(subreddit)

            submissions = [subm async for subm in subreddit.hot(limit=100)]
            submission = choice(submissions)
        except (prawexceptions.Redirect, prawexceptions.Forbidden, prawexceptions.NotFound):
            error_embed.description = "This subreddit does not exist, or is currently not accessible"
            return await msg.edit(embed=error_embed)

        if submission.over_18:
            if ctx.channel.is_nsfw():
                pass
            else:
                error_embed.description = "NSFW is only allowed in NSFW channels"
                return await msg.edit(embed=error_embed)

        # create answer embed
        finished_embed = discord.Embed(
            title=f"{submission.title}")
        finished_embed.add_field(name=f"r/{submission.subreddit}", value=f"{submission.selftext} \n \n[Link](https://reddit.com{submission.permalink})")
        finished_embed.set_thumbnail(url=submission.url)

        finished_embed.set_author(
            name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        finished_embed.set_footer(
            text=f"upvotes: {submission.score} \nreddit.com/u/{submission.author} \nuploaded: {datetime.utcfromtimestamp(submission.created_utc).strftime('%Y-%m-%d')}")

        # get comments of post
        comments = await submission.comments()
        final_comment = []
        #submission.comments.replace_more(limit=10)
        for i, comment in enumerate(comments):
            if isinstance(comment, asyncpraw.reddit.models.MoreComments):
                continue
            if i > 10:
                break
            if len(comment.body) > 1024:
                continue
            final_comment.append(comment)
            continue
        comment_int = random.randint(0,10)

        try:
            finished_embed.add_field(name="Comment", value=f"u/{final_comment[comment_int].author} \n{final_comment[comment_int].body} \nUpvotes: {final_comment[comment_int].score}", inline=False)
        except IndexError:
            return finished_embed.add_field(name="Comment", value="No comments")

        try:
            await msg.edit(embed=finished_embed)
        except commands.CommandInvokeError:
            error_embed.description = "Post too big, try again"
            return await msg.edit(embed=error_embed)

    @commands.command(aliases=["ureddit", "redditor"])
    async def reddit_user(self, ctx: commands.Context, reddit_user):
        """Search up information on a chosen redditor"""
        if reddit_user is None:
            return await ctx.reply("Give me a redditor")

        # loading embed
        loading_embed = discord.Embed(
            title="Loading...", description=f"This might take a bit... \nSubmitted by @{ctx.author}")
        msg = await ctx.reply(embed=loading_embed)

        error_embed = discord.Embed(title="ERROR", color=discord.Color.red())

        try:
            reddit_user = await self.reddit.redditor(reddit_user, fetch=True)
        except (prawexceptions.Redirect, prawexceptions.Forbidden, prawexceptions.NotFound):
            error_embed.description = "User does not exist or is banned"
            return await msg.edit(embed=error_embed)

        # making the finished embed
        finished_embed = discord.Embed(
            title=f"u/{reddit_user.name}", description=f"id: {reddit_user.id}", url=f"https://reddit.com/u/{reddit_user}")
        finished_embed.set_thumbnail(url=reddit_user.icon_img)
        finished_embed.set_author(
            name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        finished_embed.set_footer(
            text=f"Account created {datetime.utcfromtimestamp(reddit_user.created_utc).strftime('%Y-%m-%d')}")
        finished_embed.add_field(name="Comment karma",
                                 value=reddit_user.comment_karma, inline=True)
        finished_embed.add_field(
            name="Post karma", value=reddit_user.link_karma, inline=True)
        finished_embed.add_field(
            name="Reddit mod?", value=reddit_user.is_mod, inline=True)

        # check if user has any submissions
        try:
            user_subs = []
            async for submission in reddit_user.submissions.top("all"):
                user_subs.append(submission)
            top_sub = await self.reddit.submission(id=user_subs[0])
            x = await self.reddit.submission(id=user_subs[1])
            if top_sub.score < x.score:
                top_sub = x
            bottom_sub = await self.reddit.submission(id=user_subs[-1])
        except IndexError:
            return await msg.edit(embed=finished_embed)

        # loading the top and bottom submissions
        finished_embed.add_field(
            name="Top post", value=f"Upvotes: {top_sub.score} \n[Link](https://reddit.com{top_sub.permalink})", inline=False)
        finished_embed.add_field(
            name="Worst post", value=f"Upvotes: {bottom_sub.score} \n[Link](https://reddit.com{bottom_sub.permalink})", inline=False)

        await msg.edit(embed=finished_embed)


def setup(bot: commands.Bot):
    bot.add_cog(Reddit(bot))
