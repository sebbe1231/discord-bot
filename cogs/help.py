import discord
from discord.ext import commands
from itertools import groupby


class HelpCommand(commands.HelpCommand):
    # get help about the bot
    async def send_bot_help(self, _):
        bot: commands.Bot = self.context.bot

        def key(c):
            return c.cog_name or 'No Category'
        entries = await self.filter_commands(bot.commands, sort=True, key=key)

        embed = discord.Embed(title="Help", description=f"Bot made by {bot.get_user(365478245132402689)}")

        for cog, command in groupby(entries, key=key):
            if cog == "Help":
                continue

            actual_cog = bot.get_cog(cog)
            description = actual_cog.description or 'No description'
            emoji = actual_cog.emoji

            content = [description]
            content.append(f'`{self.context.prefix}help {cog}`')

            embed.add_field(name=f"{emoji} {cog}", value="\n".join(content))

        await self.context.reply(embed=embed)

    # get help about a specific category
    async def send_cog_help(self, cog: commands.Cog):
        cog_embed = discord.Embed(
            title=f"{cog.emoji} {cog.qualified_name}", description=cog.description)
        for command in cog.get_commands():
            params = ""
            for param in command.clean_params:
                params += f" <{param}>"

            command_name = command.name
            if command.aliases:
                aliases = "|".join(command.aliases)
                command_name = f"[{command.name}|{aliases}]"

            description = command.short_doc or 'No description'
            cog_embed.add_field(name=f"{command.name.capitalize()}",
                                value=f"{description} \n``{self.context.prefix}{command_name}{params}``", inline=False)

        await self.context.reply(embed=cog_embed)

    # get help on a specific command
    async def send_command_help(self, command: commands.command, error: bool = None):
        params = ""
        for param in command.clean_params:
            params += f" <{param}>"
        command_name = command.name
        if command.aliases:
            aliases = "|".join(command.aliases)
            command_name = f"[{command.name}|{aliases}]"

        command_embed = discord.Embed(
            title=f"{command.name.capitalize()}", description=f"{command.short_doc}")
        command_embed.set_author(name=f"{command.cog.qualified_name}")
        command_embed.add_field(
            name="Usage", value=f"``{self.context.prefix}{command_name}{params}``")

        msg = None
        if error:
            msg = "Incorrect usage!"
        await self.context.reply(msg, embed=command_embed)


class Help(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        bot.help_command = HelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = None


def setup(bot):
    bot.add_cog(Help(bot))
