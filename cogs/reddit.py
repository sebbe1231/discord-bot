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
        except (prawexceptions.Redirect, prawexceptions.Forbidden, prawexceptions.NotFound):
            return await msg.edit(content="This subreddit does not exist, or is currently not accessible", embed=None)

        if submission.over_18:
            if ctx.channel.is_nsfw():
                pass
            else:
                return await msg.edit(content="NSFW is only allowed in NSFW channels", embed=None)

        # create answer embed
        finished_embed = discord.Embed(
            title=f"r/{submission.subreddit}", url=f"https://reddit.com{submission.permalink}")
        if submission.is_self:
            try:
                self_text = submission.selftext
                if not self_text:
                    self_text = "_ _"
                finished_embed.add_field(
                    name=submission.title, value=self_text)
            except commands.CommandInvokeError:
                return await msg.edit(content="Post too big", embed=None)
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
            return await msg.edit(content="Post too big", embed=None)

    @commands.command(aliases=["ureddit", "redditor"])
    async def reddit_user(self, ctx: commands.Context, reddit_user):
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
        
        #making the finished embed
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
        
        #check if user has any submissions
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
            return await msg.edit(embed = finished_embed)

        #loading the top and bottom submissions
        finished_embed.add_field(
            name="Top post", value=f"Upvotes: {top_sub.score} \n[Link](https://reddit.com{top_sub.permalink})", inline=False)
        finished_embed.add_field(
            name="Worst post", value=f"Upvotes: {bottom_sub.score} \n[Link](https://reddit.com{bottom_sub.permalink})", inline=False)

        await msg.edit(embed=finished_embed)


def setup(bot: commands.Bot):
    bot.add_cog(Reddit(bot))
