import urllib.parse
from datetime import datetime

from PIL import Image, ImageFont, ImageDraw, ImageSequence
import io

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
            return await ctx.reply("There is no deffinition for that term")

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

        if len(definition) > 1024:
            definition = definition[:1019]+"\n..."
        if len(definition_ex) > 1024:
            definition_ex = definition_ex[:1019]+"\n..."

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
            return await ctx.reply("That is not a valid language option")
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
    
    @commands.command(aliases=["at"])
    async def addtext(self, ctx: commands.Context, image_link, toptext, bottomtext):
        """Add top text and or bottom text to a picture, incase top text and bottom text in " " (use image link, also works with discord image links)"""
        
        r = requests.get(image_link, stream=True)
        if r.status_code != 200:
            return await ctx.reply("Image could not be loaded")
        image = Image.open(r.raw)
        
        FONT = "./impact.ttf"
        h, w = image.size
        font_size = round(w/6)
        font = ImageFont.truetype(FONT, size=font_size)

        finished_embed = discord.Embed(description=f"[Original Image]({image_link})")
        finished_embed.set_author(name=f"Requested by {ctx.message.author.display_name}#{ctx.message.author.discriminator}", icon_url=ctx.message.author.avatar_url_as(static_format='png'))
        while True: 
            if font.getlength(toptext) >=w or font.getlength(bottomtext) >= w:
                font_size -= 1
                print(font_size)
                font = ImageFont.truetype(FONT, size=font_size)
            else:
                if hasattr(image, 'is_animated') and image.is_animated:
                    frames = []
                    for frame in ImageSequence.Iterator(image):
                        d = ImageDraw.Draw(frame)
                        d.text((h/2, w/20), text=toptext, fill=(255,255,255), anchor="mt", font=font, stroke_fill=(0, 0, 0), stroke_width=round(0.05*font_size))
                        d.text((h/2, w-(w/20)), text=bottomtext, fill=(255,)*3, anchor="ms", font=font, stroke_fill=(0, 0, 0), stroke_width=round(0.05*font_size))
                        del d
                        b = io.BytesIO()
                        frame.save(b, format="GIF")
                        frame = Image.open(b)
                        frames.append(frame)
                    frames[0].save("output.gif", save_all=True, append_images=frames[1:], format="GIF")
                    return await ctx.reply(file = discord.File("output.gif"))
                draw = ImageDraw.Draw(image)
                draw.text((h/2, w/20), text=toptext, fill=(255,)*3, anchor="mt", font=font, stroke_fill=(0, 0, 0), stroke_width=round(0.05*font_size))
                draw.text((h/2, w-(w/20)), text=bottomtext, fill=(255,)*3, anchor="ms", font=font, stroke_fill=(0, 0, 0), stroke_width=round(0.05*font_size))
                
                image.save("output.png")
            break
        return await ctx.reply(file = discord.File("output.png"))
    
    @commands.command(aliases=["avt", "pfpt", "pt"])
    async def pfptext(self, ctx: commands.Context, user: discord.User, toptext, bottomtext):
        """Add top text and or bottom text to a users avatar"""
        if toptext is None and bottomtext is None:
            return await ctx.reply("Give me something to add")
        
        image = user.avatar_url_as(static_format='png')

        try:
            r = requests.get(image, stream=True)
            if r.status_code != 200:
                raise
            image = Image.open(r.raw)
        except:
            return await ctx.reply("Image could not be loaded")

        FONT = "./impact.ttf"
        h, w = image.size
        font_size = round(w/6)
        font = ImageFont.truetype(FONT, size=font_size)

        while True: 
            if font.getlength(toptext) >=w or font.getlength(bottomtext) >= w:
                font_size -= 1
                print(font_size)
                font = ImageFont.truetype(FONT, size=font_size)
            else:
                if hasattr(image, 'is_animated') and image.is_animated:
                    frames = []
                    for frame in ImageSequence.Iterator(image):
                        d = ImageDraw.Draw(frame)
                        d.text((h/2, w/20), text=toptext, fill=(255,255,255), anchor="mt", font=font, stroke_fill=(0, 0, 0), stroke_width=round(0.05*font_size))
                        d.text((h/2, w-(w/20)), text=bottomtext, fill=(255,)*3, anchor="ms", font=font, stroke_fill=(0, 0, 0), stroke_width=round(0.05*font_size))
                        del d

                        b = io.BytesIO()
                        frame.save(b, format="GIF")
                        frame = Image.open(b)

                        frames.append(frame)
                    frames[0].save("output.gif", save_all=True, append_images=frames[1:], format="GIF")
                    return await ctx.reply(file = discord.File("output.gif"))

                draw = ImageDraw.Draw(image)
                draw.text((h/2, w/20), text=toptext, fill=(255,)*3, anchor="mt", font=font, stroke_fill=(0, 0, 0), stroke_width=round(0.05*font_size))
                draw.text((h/2, w-(w/20)), text=bottomtext, fill=(255,)*3, anchor="ms", font=font, stroke_fill=(0, 0, 0), stroke_width=round(0.05*font_size))
                
                image.save("output.png")
            break
        
        return await ctx.reply(file = discord.File("output.png"))


def setup(bot: commands.Bot):
    bot.add_cog(Funny(bot))
