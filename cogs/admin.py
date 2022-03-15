from email import message
from types import MemberDescriptorType
import discord
from discord.ext import commands


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context):
        #admin = discord.Member.guild_permissions.administrator
        return ctx.author.guild_permissions.administrator

    @commands.command()
    async def admin(self, ctx: commands.Context):
        print(ctx.author)
        await ctx.reply("You are an admin!")

    @commands.command(aliases = ["m"])
    async def mute(self, ctx: commands.Context, user: discord.Member = None):
        if user is None:
            role = discord.utils.get(ctx.message.guild.roles, name="muted")
            user = ctx.message.author
            await user.add_roles(role)
            await ctx.send(f"User: {user}, has been muted")
        else:
            role = discord.utils.get(ctx.message.guild.roles, name="muted")
            await user.add_roles(role)
            await ctx.send(f"User: {user}, has been muted")

    @commands.command(aliases = ["un"])
    async def unmute(self, ctx: commands.Context, user: discord.Member = None):
        if user is None:
            role = discord.utils.get(ctx.message.guild.roles, name="muted")
            user = ctx.message.author
            await user.remove_roles(role)
            await ctx.send(f"User: {user}, has been unmuted")
        else:
            role = discord.utils.get(ctx.message.guild.roles, name="muted")
            await user.remove_roles(role)
            await ctx.send(f"User: {user}, has been unmuted")

    @commands.command()
    async def nuke(self, ctx: commands.Context):
        await ctx.send("** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ")


def setup(bot: commands.Bot):
    bot.add_cog(Admin(bot))
