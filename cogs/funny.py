from gettext import translation
from turtle import title
from unicodedata import name
from aiohttp import request
import discord
from discord.ext import commands
from googletrans import Translator
from parso import parse
import requests
import urllib.parse
from datetime import datetime

from setuptools import Command
from tr import langs

class Funny(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx: commands.Context):
        await ctx.send(ctx.message.author.mention)

    @commands.command()
    async def bitches(self, ctx: commands.Context, user: discord.User = None):
        await ctx.message.delete()
        
        if user is None:
            return await ctx.send("https://tenor.com/view/foss-no-bitches-no-hoes-0bitches-no-gif-24529727")
        
        await ctx.send(f"{user.mention}\nhttps://tenor.com/view/foss-no-bitches-no-hoes-0bitches-no-gif-24529727")

    @commands.command(aliases=['urban', 'ud'])
    async def urbandictionary(self, ctx: commands.Context, *, term):
        term = urllib.parse.quote(term)
        r = requests.get(
            f'https://api.urbandictionary.com/v0/define?term={term.lower()}')

        x = r.json()['list'][0]
        

        # ['definition', 'permalink', 'thumbs_up', 'sound_urls', 'author',
        #     'word', 'defid', 'current_vote', 'written_on', 'example', 'thumbs_down']

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
    async def translate(self, ctx: commands.Context, language, *, text = None):
        if text is None:
            await ctx.reply("Give me something to translate! >:(")
            return
        translator = Translator(service_urls = ['translate.google.com'])
        translation = translator.translate(str(text), dest = language)
        #await ctx.reply(translation.text)
        source = translation.src
        output = translation.dest
        embed = discord.Embed(title = "Translation complete!", color=0xff00f2, text = "translate.google.com")
        embed.add_field(name = "Translated from:", value = langs.get(source, 'unknown'), inline=True)
        embed.add_field(name = "Translated to:", value = langs.get(output, 'unknown'), inline = True)
        embed.add_field(name = "Source:", value = text, inline = False)
        embed.add_field(name = "Result:", value = translation.text, inline = False)

        await ctx.reply(embed=embed)
    
    @commands.command(aliases = ["transen", "gten"])
    async def englishtranslate(self, ctx: commands.Context, *, text = None):
        return await self.translate(ctx, 'en', text=text)
    
    @translate.error
    async def translate_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.reply("Tell me a language in the start \n .gt [language] [To be translated] \n or use .gten")

    @urbandictionary.error
    async def urbandictionary_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply("Say something to define :)")    


    @bitches.error
    async def bitches_error(self, ctx: commands.Context,
                            error: discord.DiscordException):
        if isinstance(error, commands.UserNotFound):
            return await ctx.send("User does not exist? Pog")

        raise error


def setup(bot: commands.Bot):
    bot.add_cog(Funny(bot))
