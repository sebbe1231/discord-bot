import discord
from discord.ext import commands

keywords = [
    ["linux", "https://tenor.com/view/linux-stfu-linux-user-destroyed-owned-gif-22882406"],
    ["ratio", "counter ratio"]
]
keywords2 = [
    ["sweden", "sverige", "swede", "svensk"]
]

class Detection(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id == self.bot.user.id:
            return

        if not message.content.startswith("."):
            #print(message.content)
            lmessage = message.content
            lmessage = lmessage.lower()
            for kw in keywords:
                if kw[0] in lmessage:
                    await message.reply(kw[1])
            #sweden
            for kw in keywords2[0]:
                if kw in lmessage:
                    user = message.author
                    role = discord.utils.get(message.guild.roles, name = "muted")
                    await user.add_roles(role)
                    await message.delete()


def setup(bot: commands.Bot):
    bot.add_cog(Detection(bot))