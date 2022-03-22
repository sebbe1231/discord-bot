import urllib.parse
from datetime import datetime

import discord
import requests
from discord.ext import commands
from googletrans import Translator
from tr import langs


class Funny(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.emoji = ":clown:"

    @commands.command()
    async def bitches(self, ctx: commands.Context, user: discord.User = None):
        """no bitches?"""
        await ctx.message.delete()
        
        if user is None:
            return await ctx.send("https://tenor.com/view/foss-no-bitches-no-hoes-0bitches-no-gif-24529727")
        
        await ctx.send(f"{user.mention}\nhttps://tenor.com/view/foss-no-bitches-no-hoes-0bitches-no-gif-24529727")

    @commands.command(aliases=['urban', 'ud'])
    async def urbandictionary(self, ctx: commands.Context, *, term):
        """Search up a term in urbandictionary.com"""
        try:
            term = urllib.parse.quote(term)
            r = requests.get(
                f'https://api.urbandictionary.com/v0/define?term={term.lower()}')

            x = r.json()['list'][0]
        except IndexError:
            return await ctx.reply(f"There is no deffinition for that term")

        definition = x['definition']
        definition_link = x['permalink']
        likes = x['thumbs_up']
        dislikes = x['thumbs_down']
        author = x['author']
        def_word = x['word']
        
        def_date = x['written_on'][:-14]
        def_date = datetime.strptime(def_date, "%Y-%m-%d")
        def_date = def_date.strftime("%B %e, %Y")

        definition_ex = x['example']

        embed = discord.Embed(
            title=def_word.capitalize(),
            url=definition_link,
            description=definition,
            color=0xff00f2,
        )
        embed.add_field(name ="Example", value = f"{definition_ex}", inline = False)
        embed.add_field(name ="Author", value = author, inline = True)
        embed.add_field(name = "Votes", value = f"likes: {likes} \n dislikes: {dislikes}")
        embed.set_footer(text = def_date)

        await ctx.reply(embed=embed)


    @commands.command(aliases=["trans", "gt"])
    async def translate(self, ctx: commands.Context, language, *, text):
        """Translate sentence to chosen language, it auto detects your input."""
        #return await ctx.reply("This function does not work yet sadge")
        if text is None:
            await ctx.reply("give me a language to translate to, and something to translate ``.translate [language] <text>``")
            return

        try:
            translator = Translator()
            translation = translator.translate(text=str(text), dest=language)
        except ValueError:
            return await ctx.reply(f"**{language}** is not a valid language option")
        #await ctx.reply(translation.text)
        source = translation.src
        output = translation.dest
        embed = discord.Embed(title = "Translation complete!", color=0xff00f2, text = "translate.google.com")
        embed.add_field(name = "Translated from:", value = langs.get(source, 'unknown'), inline=True)
        embed.add_field(name = "Translated to:", value = langs.get(output, 'unknown'), inline = True)
        embed.add_field(name = "Source:", value = text, inline = False)
        embed.add_field(name = "Result:", value = translation.text, inline = False)

        await ctx.reply(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Funny(bot))
