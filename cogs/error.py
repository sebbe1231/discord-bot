from discord.ext import commands


class Error(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CheckFailure):
            return await ctx.reply("Missing perms.")
        elif isinstance(error, commands.UserNotFound):
            return await ctx.reply("User does not exist? Pog")
        elif isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            help_command = self.bot.help_command
            help_command.context = ctx
            return await help_command.send_command_help(ctx.command, True)
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.reply(f"""Hmmm something went wrong, check your message,
                 and use {ctx.prefix}`help <command>` to see needed arguments. 
                Or maybe the developer is just a dumbass""")
        elif isinstance(error, commands.MemberNotFound):
            return await ctx.reply("Member not found")
        elif isinstance(error, commands.BadBoolArgument):
            return await ctx.reply("Not a valid bool value")
        raise error

def setup(bot: commands.Bot):
    bot.add_cog(Error(bot))