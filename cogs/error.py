import discord
from discord.ext import commands

class Error(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CheckFailure):
            return await ctx.reply("Missing perms L :joy: :skull: :joy: :skull:")
        elif isinstance(error, commands.UserNotFound):
            return await ctx.reply("User does not exist? Pog")
        elif isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.reply("You're missing an argument, use `.help <command>` to see what is needed")
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.reply("Hmmm something went wrong, check your message, and use `.help <command>` to see needed arguments. Or maybe the developer is just a dumbass")
            
            

        raise error

def setup(bot: commands.Bot):
    bot.add_cog(Error(bot))