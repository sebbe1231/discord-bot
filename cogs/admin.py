from ast import Str, With
from math import perm
from multiprocessing import AuthenticationError
import discord
from discord.ext import commands
import sqlite3
from datetime import datetime, timedelta
from sqlalchemy import DateTime, and_
from sqlalchemy.orm import Session
from database import User, Warning, engine

class Admin(commands.Cog):
    """Commands for admin and admin like perms only"""
    def __init__(self, bot):
        self.bot = bot
        self.emoji = ":shield:"
    

    @commands.command(aliases = ["m"])
    async def mute(self, ctx: commands.Context, user: discord.Member = None):
        """Mute a user"""
        if not await Admin.CheckPerm(ctx=ctx, perm="mute"):
            await ctx.reply("Missing perms")
            return
        
        if user is None:
            user = ctx.message.author
        role = discord.utils.get(ctx.message.guild.roles, name="muted")
        await user.add_roles(role)
        await ctx.send(f"User: {user}, has been muted")

    @commands.command(aliases = ["um"])
    async def unmute(self, ctx: commands.Context, user: discord.Member = None):
        """Unmute a user"""
        if not await Admin.CheckPerm(ctx=ctx, perm="mute"):
            await ctx.reply("Missing perms")
            return

        print(user)
        if user is None:
            user = ctx.message.author
        role = discord.utils.get(ctx.message.guild.roles, name="muted")
        await user.remove_roles(role)
        await ctx.send(f"User: {user}, has been unmuted") 

    @commands.command()  
    async def warn(self, ctx: commands.Context, user: discord.Member, perma: bool, *, reason):
        """warn a user. Perma: True/False"""
        if not await Admin.CheckPerm(ctx=ctx, perm="warn"):
            await ctx.reply("Missing perms")
            return

        current_time = datetime.utcnow()
        with Session(engine) as session:
            add_warn = Warning(
                reason=reason,
                warned_user_id=user.id,
                warned_by_user_id=ctx.author.id,
                warn_date = current_time,
                expire_date = current_time + timedelta(minutes=1),
                perma = perma,
                guild_id = ctx.message.guild.id
            )
            session.add(add_warn)
            session.commit()
        
        await ctx.reply("User has been warned")
    
    @commands.command()
    async def warns(self, ctx: commands.Context, user: discord.Member):
        """See the warns of a user"""
        if not await Admin.CheckPerm(ctx=ctx, perm="warn"):
            await ctx.reply("Missing perms")
            return

        with Session(engine) as session:
            print(User.user_id(user.id).warnings)
            #print(session.query(Warning).filter_by(warned_user_id = user.id).all())

        # user = ctx.message.guild.get_member(user.id)
        # conn = sqlite3.connect(f"./cogs/db_strg/{ctx.guild.id}.db")
        # c = conn.cursor()

        # embed = discord.Embed(title=f"Warns for user {user.display_name}#{user.discriminator}", description=f"ID: {user.id}")
        # embed.set_thumbnail(url=user.avatar_url)

        # for row in c.execute(f'SELECT rowid, * FROM warns WHERE user_id={user.id}'):
        #     if row[6] == 1:
        #         exp = "Never"
        #     else:
        #         exp = row[5]
        #     embed.add_field(name=f"Warn ID: {row[0]}", value=f"{row[4]} \n \n{row[2]} ({ctx.message.guild.get_member(row[3]).display_name}#{ctx.message.guild.get_member(row[3]).discriminator}) \nExpires: {exp}", inline=False)
        
        # await ctx.reply(embed=embed)

        # conn.close()
    
    @commands.command()
    async def deletewarn(self, ctx: commands.Context, warn_id):
        """Delete warn"""
        if not await Admin.CheckPerm(ctx=ctx, perm="warn"):
            await ctx.reply("Missing perms")
            return

        conn = sqlite3.connect(f"./cogs/db_strg/{ctx.guild.id}.db")
        c = conn.cursor()

        c.execute(f"""DELETE FROM warns WHERE rowid = {warn_id}""")
        await ctx.reply("Warn deleted.")

        conn.commit()
        conn.close()

    @commands.command()
    async def delmessagelog(self, ctx: commands.Context):
        """Logs of deleted messages"""
        if not await Admin.CheckPerm(ctx=ctx, perm="mute"):
            await ctx.reply("Missing perms")
            return

        if not ctx.author.guild_permissions.manage_messages:
            return await ctx.reply("Missing perms")
        
        conn = sqlite3.connect(f"./cogs/db_strg/{ctx.guild.id}.db")
        c = conn.cursor()

        for row in c.execute('SELECT * FROM chat_logs'):
            await ctx.send(row)
        
        conn.close()

    @commands.command()
    async def purge(self, ctx: commands.Context, purge_limit):
        """Purge a specific amount of messages"""
        if not await Admin.CheckPerm(ctx=ctx, perm="purge"):
            await ctx.reply("Missing perms")
            return

        try:
            await ctx.message.delete()
            purge_limit = int(purge_limit)
        except ValueError:
            return await ctx.reply("Not a valid limit")

        deleted = await ctx.channel.purge(limit = purge_limit)
        await ctx.send(f"Deleted {len(deleted)} message(s)")

def setup(bot: commands.Bot):
    bot.add_cog(Admin(bot))
