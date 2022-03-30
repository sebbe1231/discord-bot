import re
from os import environ

import discord
import tweepy
from discord.ext import commands
from tweepy import OAuthHandler

auth = OAuthHandler(environ['TWITTER_KEY'], environ['TWITTER_KEY_SECRET'])
auth.set_access_token(environ['TWITTER_ACCESS_TOKEN'],
                      environ['TWITTER_ACCESS_TOKEN_SECRET'])
api = tweepy.API(auth, wait_on_rate_limit=True)


class Twitter(commands.Cog):
    """Commands using the twitter API"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.emoji = ":bird:"

    @commands.command(aliases=["tp"])
    async def twitterprofile(self, ctx: commands.Context, user):
        """Search for a twitter user"""
        #check if input is valid
        try:
            if re.match(r'[0-9]{16,}', user):
                user = api.get_user(user_id=user)
            elif len(user) <= 15:
                user = api.get_user(screen_name=user)
            else:
                return await ctx.reply("Not a valid user")
        except tweepy.errors.Forbidden:
            return await ctx.reply("user has been suspended")
        except tweepy.errors.NotFound:
            return await ctx.reply("user does not exist")

        user_name_id = f"{user.name} (@{user.screen_name})"
        if user.verified:
            user_name_id = f"{user.name} :white_check_mark: (@{user.screen_name})"

        # creating da embed
        twitter_embed = discord.Embed(
            title=user_name_id, description=f"{user.description} \n[Link](https://twitter.com/{user.screen_name})")
        twitter_embed.set_thumbnail(url=user.profile_image_url)
        twitter_embed.set_author(name=f"ID: {user.id_str}")
        twitter_embed.add_field(
            name="Followers", value=user.followers_count, inline=True)
        twitter_embed.add_field(
            name="Following", value=user.friends_count, inline=True)
        twitter_embed.add_field(
            name="Tweets", value=user.statuses_count, inline=True)
        if user.location:
            twitter_embed.add_field(
                name="Location", value=user.location, inline=True)
        
        #add an embed field of users most recent tweets, but only if they have any
        if len(api.user_timeline(user_id=user.id_str)) > 0:
            recent_tweet = api.user_timeline(
                user_id=user.id_str, include_rts=False, exclude_replies=True, count=1)
            for tweet in recent_tweet:
                newest_tweet = tweet

            s_text = re.sub(
                r"(@([A-Za-z0-9_]{4,15}))",
                r"[\1](https://twitter.com/\2)",
                newest_tweet.text
            )
            twitter_embed.add_field(
                name="Most recent Tweet", value=f"{s_text} \n \n:heart: {newest_tweet.favorite_count} \n{str(newest_tweet.created_at)[:-14]}", inline=False)
        
        #find acc creation date
        twitter_embed.set_footer(
            text=f"https://twitter.com/{user.screen_name} \nAccount creation date: {str(user.created_at)[:-14]}")

        #send da embed
        await ctx.reply(embed=twitter_embed)


def setup(bot: commands.Bot):
    bot.add_cog(Twitter(bot))
