from cProfile import Profile
import discord
from discord.ext import commands


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases = ["av"])
    async def avatar(self, ctx: commands.Context, user: discord.User = None):
        if user is None:
            user = ctx.message.author
            await ctx.reply(user.avatar_url_as(static_format='png'))

        else:
            await ctx.reply(user.avatar_url_as(static_format='png'))

    # https://discordpy.readthedocs.io/en/stable/api.html?highlight=user#discord.User.history
    # https://discordpy.readthedocs.io/en/stable/api.html?highlight=user#discord.User
    @commands.command(aliases=["p"])
    async def profile(self, ctx: commands.Context, user: discord.Member = None):
        if user is None:
            user = ctx.message.author

        user_name = f"{user.name}#{user.discriminator}"
        create_date = str(user.created_at)[:-15]
        joined_date = str(user.joined_at)[:-15]         
        
        # Embed creation
        embed = discord.Embed(title=user_name, color=0xff00f2)
        embed.set_thumbnail(url=user.avatar_url)
        
        embed.add_field(name="Nickname", value=user.nick, inline=True)
        embed.add_field(name="User ID", value=user.id, inline=True)
        embed.add_field(name="Status", value=user.status, inline=False)
        embed.add_field(name="Account creation date",
                        value=create_date, inline=True)
        embed.add_field(name="Join server date",
                        value=joined_date, inline=True)
        
        if user.bot == True:
            embed.set_footer(text = "THIS IS A BOT")

        await ctx.reply(embed=embed)

def setup(bot: commands.Bot):
    bot.add_cog(Profile(bot))
