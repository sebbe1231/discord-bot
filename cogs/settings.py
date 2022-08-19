import string
import discord
from discord.ext import commands
from datetime import datetime, timedelta
import humanfriendly
from psycopg2 import DataError
import sqlalchemy
from sqlalchemy.orm import Session
from database import DelMessageLog, User, GuildData, Warning, engine

class Settings(commands.Cog):
    """Server settings for the bot (Owner only)"""
    def __init__(self, bot):
        self.bot = bot
        self.emoji = ":gear:"
    
    async def cog_check(self, ctx: commands.Context):
        return ctx.author == ctx.guild.owner
    
    @commands.command()
    async def changeprefix(self, ctx: commands.Context, prefix):
        with Session(engine) as session:
            prefix_update = session.query(GuildData).filter(GuildData.guild_id == ctx.message.guild.id).first()
            prefix_update.bot_prefix = str(prefix)
            session.commit()
        
        await ctx.reply("Prefix has been changed!")
    
    @commands.command()
    async def roleperms(self, ctx:commands.Context):
        """Get an overlook over how the roleperms are structured"""
        embed = discord.Embed(
            title="Role permission overlook",
            description="If you want a given role to have access to a given command, you most give said role permissions as shown bellow"
        )
        embed.add_field(name="Permission: Ban Members", value = f"Access to: \n`{ctx.prefix}ban` \n`{ctx.prefix}unban`")
        embed.add_field(name="Permission: Kick Members", value=f"Access to: \n`{ctx.prefix}kick`")
        embed.add_field(name="Permission: Timeout Members", value=f"Access to: \n`{ctx.prefix}mute` \n`{ctx.prefix}unmute`")
        embed.add_field(name="Permission: Manage Roles", value=f"Access to: \n`{ctx.prefix}warn` \n`{ctx.prefix}deletewarn` \n`{ctx.prefix}warns`")
        embed.add_field(name="Permission: View Audit Log", value=f"Access to: \n`{ctx.prefix}delmessagelog` \n`{ctx.prefix}purge`")

        await ctx.reply(embed=embed)
    
    @commands.command()
    async def muterole(self, ctx:commands.Context, mute_id):
        """Specify the muterole id"""
        with Session(engine) as session:
            mute_update = session.query(GuildData).filter(GuildData.guild_id == ctx.message.guild.id).first()
            try:
                mute_role = ctx.guild.get_role(int(mute_id))
            except ValueError:
                return await ctx.reply("Not a valid id")

            if mute_role is None:
                return await ctx.reply("The mute role id does not seem to fit any role on the server.")

            mute_update.mute_role_id = mute_id
            session.commit()
                        
            await ctx.reply(f"{mute_role} is now the role that users get in relation to the mute command")   

    @commands.command()
    async def warnduration(self, ctx: commands.Context, duration):
        """Change the duration of warns"""
        try:
            time = humanfriendly.parse_timespan(duration)
        except humanfriendly.InvalidTimespan:
            return await ctx.reply("Now a valid time")

        with Session(engine) as session:
            warn_length_update = session.query(GuildData).filter(GuildData.guild_id == ctx.message.guild.id).first()
            warn_length_update.warn_length = time
            session.commit()
        
        await ctx.reply(f"Warn duration changed to {humanfriendly.format_timespan(time)}")

    @commands.command(aliases = ["cs"])
    async def checksettings(self, ctx: commands.Context):
        """See your server's settings and guild data"""
        with Session(engine) as session:
            embed = discord.Embed(title=f"Data for: {ctx.message.guild}")
            embed.add_field(name="Bot prefix", value=f"{session.query(GuildData.bot_prefix).filter(GuildData.guild_id == ctx.message.guild.id).scalar()}")
            embed.add_field(name="Mute role", value=f"{discord.utils.get(ctx.message.guild.roles, id=session.query(GuildData.mute_role_id).filter(GuildData.guild_id == ctx.message.guild.id).scalar())} ({session.query(GuildData.mute_role_id).filter(GuildData.guild_id == ctx.message.guild.id).scalar()})")
            embed.add_field(name="Warn duration", value=f"{humanfriendly.format_timespan(session.query(GuildData.warn_length).filter(GuildData.guild_id == ctx.message.guild.id).scalar())}")

        await ctx.reply(embed=embed)

        
def setup(bot: commands.Bot):
    bot.add_cog(Settings(bot))