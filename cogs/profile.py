from cProfile import Profile
import discord
from discord.ext import commands
from datetime import datetime


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = ":man:"

    @commands.command(aliases = ["av"])
    async def avatar(self, ctx: commands.Context, user: discord.User = None):
        """Get the avatar of a given user (Works for users not in the server too)"""
        if user is None:
            user = ctx.message.author
            await ctx.reply(user.avatar_url_as(static_format='png'))

        else:
            await ctx.reply(user.avatar_url_as(static_format='png'))

    # https://discordpy.readthedocs.io/en/stable/api.html?highlight=user#discord.User.history
    # https://discordpy.readthedocs.io/en/stable/api.html?highlight=user#discord.User
    @commands.command(aliases=["p"])
    async def profile(self, ctx: commands.Context, user: discord.Member = None):
        """Get information about a discord user in the server"""
        if user is None:
            user = ctx.message.author

        user_name = f"{user.name}#{user.discriminator}"
        create_date = str(user.created_at)[:-15]
        joined_date = str(user.joined_at)[:-15]         
        status = user.status
        activity = "No activity"

        # Embed creation
        embed = discord.Embed(title=user_name, color=0xff00f2)
        embed.set_thumbnail(url=user.avatar_url)
        
        embed.add_field(name="Nickname", value=user.nick, inline=True)
        embed.add_field(name="User ID", value=user.id, inline=True)
        
        for s in user.activities:
            if isinstance(s, discord.CustomActivity):
                status = f"{user.status} - {s}"
                embed.add_field(name="Status", value=status, inline=False)
                continue
            activity = s
            if activity.type == discord.ActivityType.playing:
                started_at = datetime.fromtimestamp(activity.timestamps['start']/1000)
                difference = str(datetime.now()-started_at)[:-7]
                print("playing")
                embed.add_field(name="Playing", value=f"**{activity.name}** \n{activity.details} \n{difference} \n{activity.large_image_text}", inline=False)
            if activity.type == discord.ActivityType.listening:
                embed.add_field(name="Listening", value=f"**{activity.name}** \nArtist: {activity.artist} \nSong: {activity.title} \nDuration: {str(activity.duration)[:-7]}")

        if status is user.status:
            embed.add_field(name="Status", value=status, inline=False)
        embed.add_field(name="Account creation date",
                        value=create_date, inline=True)
        embed.add_field(name="Join server date",
                        value=joined_date, inline=True)
        
        if user.bot == True:
            embed.set_footer(text = "THIS IS A BOT")

        await ctx.reply(embed=embed)

def setup(bot: commands.Bot):
    bot.add_cog(Profile(bot))
