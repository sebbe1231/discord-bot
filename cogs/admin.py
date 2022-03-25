import discord
from discord.ext import commands


class Admin(commands.Cog):
    """Commands for admins only"""
    def __init__(self, bot):
        self.bot = bot
        self.emoji = ":shield:"

    async def cog_check(self, ctx: commands.Context):
        #admin = discord.Member.guild_permissions.administrator
        return ctx.author.guild_permissions.administrator

    @commands.command()
    async def admin(self, ctx: commands.Context):
        """Test to see if you are admin"""
        print(ctx.author)
        await ctx.reply("You are an admin!")

    @commands.command(aliases = ["m"])
    async def mute(self, ctx: commands.Context, user: discord.Member = None):
        """Mute a user"""
        if user is None:
            role = discord.utils.get(ctx.message.guild.roles, name="muted")
            user = ctx.message.author
            await user.add_roles(role)
            await ctx.send(f"User: {user}, has been muted")
        else:
            role = discord.utils.get(ctx.message.guild.roles, name="muted")
            await user.add_roles(role)
            await ctx.send(f"User: {user}, has been muted")

    @commands.command(aliases = ["um"])
    async def unmute(self, ctx: commands.Context, user: discord.Member = None):
        """Unmute a user"""
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
        """Clear chat"""
        await ctx.send("** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ** **\n ")
        await ctx.message.delete()

    @commands.command()
    async def purge(self, ctx: commands.Context, purge_limit):
        """Purge a specific amount of messages"""
        try:
            await ctx.message.delete()
            purge_limit = int(purge_limit)
        except ValueError:
            return await ctx.reply("Not a valid limit")

        deleted = await ctx.channel.purge(limit = purge_limit)
        await ctx.send(f"Deleted {len(deleted)} message(s)")

def setup(bot: commands.Bot):
    bot.add_cog(Admin(bot))
