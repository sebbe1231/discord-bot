import urllib.parse
from datetime import datetime

import discord
import requests
from discord.ext import commands
from googletrans import Translator
from tr import langs

import re

class Funny(commands.Cog):
    """The best commands"""
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

        if len(definition) > 1024:
            definition = definition[:1019]+"\n..."
        if len(definition_ex) > 1024:
            definition_ex = definition_ex[:1019]+"\n..."
        
        #make clickable ref links in definition
        m_definition = re.findall(
            r"(\[(.*?)\])",
            definition
        )
        for defi in m_definition:
            definition = definition.replace(defi[0], 
            f"{defi[0]}(https://www.urbandictionary.com/define.php?term={urllib.parse.quote(defi[1])})")

        #make clickable ref links in example
        m_example = re.findall(
            r"(\[(.*?)\])",
            definition_ex
        )
        for examp in m_example:
            definition_ex = definition_ex.replace(examp[0],
            f"{examp[0]}(https://www.urbandictionary.com/define.php?term={urllib.parse.quote(examp[1])})")

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
        if text is None:
            await ctx.reply("give me a language to translate to, and something to translate ``.translate [language] <text>``")
            return

        try:
            translator = Translator()
            translation = translator.translate(text=str(text), dest=language)
        except ValueError:
            return await ctx.reply(f"That is not a valid language option")
        #await ctx.reply(translation.text)
        source = translation.src
        output = translation.dest

        result_text = translation.text
        if len(result_text) > 1024:
            result_text = result_text[1019]+"\n..."
        if len(text) > 1024:
            text = text[1019]+"\n..."

        embed = discord.Embed(title = "Translation complete!", color=0xff00f2, text = "translate.google.com")
        embed.add_field(name = "Translated from:", value = langs.get(source, 'unknown'), inline=True)
        embed.add_field(name = "Translated to:", value = langs.get(output, 'unknown'), inline = True)
        embed.add_field(name = "Source:", value = text, inline = False)
        embed.add_field(name = "Result:", value = translation.text, inline = False)

        await ctx.reply(embed=embed)
    
    @commands.command(aliases = ["transsrc", "gtsrc"])
    async def translatesrc(self, ctx: commands.Context, language_src, language_dest, *, text):
        """Translate something with a given source language and destination language"""
        if text is None:
            await ctx.reply("give me a language to translate to, and something to translate ``.help translatesrc``")
            return

        try:
            translator = Translator()
            translation = translator.translate(text=str(text), dest=language_dest, src=language_src)
        except ValueError:
            return await ctx.reply(f"That is not a valid language option")
        
        source = translation.src
        output = translation.dest
        result_text = translation.text
        if len(result_text) > 1024:
            result_text = result_text[1019]+"\n..."
        if len(text) > 1024:
            text = text[1019]+"\n..."

        embed = discord.Embed(title = "Translation complete!", color=0xff00f2, text = "translate.google.com")
        embed.add_field(name = "Translated from:", value = langs.get(source, 'unknown'), inline=True)
        embed.add_field(name = "Translated to:", value = langs.get(output, 'unknown'), inline = True)
        embed.add_field(name = "Source:", value = text, inline = False)
        embed.add_field(name = "Result:", value = translation.text, inline = False)

        await ctx.reply(embed=embed)

def setup(bot: commands.Bot):
    bot.add_cog(Funny(bot))
