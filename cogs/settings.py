from turtle import title
from winreg import KEY_CREATE_LINK
import discord
from discord.ext import commands
import sqlite3
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import DelMessageLog, User, GuildData, Warning, engine

class Settings(commands.Cog):
    """Server settings for the bot (Administrator perms only)"""
    def __init__(self, bot):
        self.bot = bot
        self.emoji = ":gear:"
    
    async def cog_check(self, ctx: commands.Context):
        return ctx.author == ctx.guild.owner
    
    @commands.command()
    async def changeprefix(self, ctx: commands.Context, prefix):
        with Session(engine) as session:
            prefix_update = session.query(GuildData).filter(GuildData.guild_id == ctx.message.guild.id).first()
            prefix_update.bot_prefix = prefix
            session.commit()
    
    @commands.command()
    async def roleperms(self, ctx:commands.Context):
        """Get an overlook over how the roleperms look"""
        embed = discord.Embed(
            title="Role permission overlook",
            description="If you want a given role to have access to a given command, you most give said role permissions as shown bellow"
        )
        embed.add_field(name="Permission: Ban Members", value = f"Access to: \n`{ctx.prefix}ban` \n`{ctx.prefix}unban`")
        embed.add_field(name="Permission: Kick Members", value=f"Access to: \n`{ctx.prefix}kick`")
        embed.add_field(name="Permission: Manage Messages", value=f"Access to: \n`{ctx.prefix}mute` \n`{ctx.prefix}unmute`")
        embed.add_field(name="Permission: Manage Roles", value=f"Access to: \n`{ctx.prefix}warn` \n`{ctx.prefix}deletewarn` \n`{ctx.prefix}warns`")
        embed.add_field(name="Permission: View Audit Log", value=f"Access to: \n`{ctx.prefix}delmessagelog` \n`{ctx.prefix}purge`")

        await ctx.reply(embed=embed)
        
def setup(bot: commands.Bot):
    bot.add_cog(Settings(bot))