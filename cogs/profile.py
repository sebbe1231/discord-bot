import discord
from discord.ext import commands
from datetime import datetime


class Profile(commands.Cog):
    """Get profile information about discord users"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.emoji = ":man:"

    @commands.command(aliases=["av"])
    async def avatar(self, ctx: commands.Context, user: discord.User = None):
        """Get the avatar of a given user (Works for users not in the server too)"""
        if user is None:
            user = ctx.message.author

        await ctx.reply(user.avatar_url_as(static_format='png'))

    # https://discordpy.readthedocs.io/en/stable/api.html?highlight=user#discord.User.history
    # https://discordpy.readthedocs.io/en/stable/api.html?highlight=user#discord.User
    @commands.command(aliases=["p", "whois"])
    async def profile(self, ctx: commands.Context, user: discord.User = None):
        """Get information about a discord user in or out of the server"""
        if user is None:
            user = ctx.message.author
        
        member = ctx.message.guild.get_member(user.id)
        if member is None:
            finished_embed = discord.Embed(title=f"{user.display_name}#{user.discriminator}", description=f"**ID:** \n{user.id}")
            finished_embed.set_author(name="Basic profile")
            finished_embed.set_image(url = user.avatar_url)
            if user.bot:
                finished_embed.set_footer("THIS IS A BOT")

            await ctx.reply(embed=finished_embed)
            return

        user_name = f"{member.name}#{member.discriminator}"
        create_date = str(member.created_at)[:-15]
        joined_date = str(member.joined_at)[:-15]
        status = member.status
        activity = "No activity"

        # Embed creation
        embed = discord.Embed(title=user_name, color=0xff00f2)
        embed.set_thumbnail(url=member.avatar_url)

        embed.add_field(name="Nickname", value=member.nick, inline=True)
        embed.add_field(name="User ID", value=member.id, inline=True)

        for s in member.activities:
            if isinstance(s, discord.CustomActivity):
                status = f"{member.status} - {s}"
                embed.add_field(name="Status", value=status, inline=False)
                continue
            activity = s
            if activity.type == discord.ActivityType.playing:
                started_at = datetime.fromtimestamp(
                    activity.timestamps['start']/1000)
                difference = str(datetime.now()-started_at)[:-7]
                embed.add_field(
                    name="Playing", value=f"**{activity.name}** \n{activity.details} \n{difference} \n{activity.large_image_text}", inline=False)
            if activity.type == discord.ActivityType.listening:
                embed.add_field(
                    name="Listening",
                    value=f"**{activity.name}** \nArtist: {activity.artist} \nSong: {activity.title} \nDuration: {str(activity.duration)[:-7]}",
                    inline=False
                )

        if status is member.status:
            embed.add_field(name="Status", value=status, inline=False)
        embed.add_field(name="Account creation date",
                        value=create_date, inline=True)
        embed.add_field(name="Join server date",
                        value=joined_date, inline=True)

        if member.bot:
            embed.set_footer(text="THIS IS A BOT")

        await ctx.reply(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Profile(bot))
