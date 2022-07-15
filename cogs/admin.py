import asyncio
import discord
from discord.ext import commands
from datetime import datetime, timedelta
from sqlalchemy import DateTime, and_
from sqlalchemy.orm import Session
from database import DelMessageLog, GuildUserPunishment, GuildData, User, Warning, engine
import humanfriendly

class Admin(commands.Cog):
    """Commands for admin and admin like perms only"""
    def __init__(self, bot):
        self.bot = bot
        self.emoji = ":shield:"
    
    async def add_punishment(user, punisher, guild, type, reason, duration):
        with Session(engine) as session:
            add_punish = GuildUserPunishment(
                guild_id = guild,
                user_id = user,
                punisher_id = punisher,
                type = type,
                reason = reason,
                duration = duration,
                punish_date = datetime.utcnow()
            )
            session.add(add_punish)
            session.commit()


    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, user: discord.Member, duration=None, *, reason=None):
        """Ban a user. Example of duration 5m = 5 minutes"""
        try:
            time = humanfriendly.parse_timespan(duration)
        except humanfriendly.InvalidTimespan:
            reason = duration + " " + reason

            #Add ban to punishment database
            await Admin.add_punishment(user.id, ctx.message.author.id, ctx.message.guild.id, "Ban", reason, "Perma")
            
            #Actual banning process
            await ctx.guild.ban(user, reason=reason)
            return await ctx.reply(f"{user} has been banned for **unlimited time**. Reason: **{reason}**")

        #Add ban to punishment database
        await Admin.add_punishment(user.id, ctx.message.author.id, ctx.message.guild.id, "Ban", reason, humanfriendly.format_timespan(time))

        # Actual banning process
        await ctx.reply(f"{user} has been banned for **{humanfriendly.format_timespan(time)}**. Reason: **{reason}**")
        await ctx.guild.ban(user, reason=reason)
        await asyncio.sleep(time)
        await ctx.guild.unban(user)
        await ctx.send(f"{user} has been unbanned")
    
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx: commands.Context, user: discord.User):
        """Unban a user"""
        try:
            await ctx.guild.unban(user)
        except discord.errors.NotFound:
            return await ctx.reply("User is not banned")
        await ctx.reply(f"{user} has been unbanned")
    
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, user: discord.Member, *, reason=""):
        await Admin.add_punishment(user.id, ctx.message.author.id, ctx.message.guild.id, "Kick", reason, None)
        
        await ctx.guild.kick(user, reason=reason)
        await ctx.send(f"{user} has been kicked. Reason: **{reason}**")

    @commands.command(aliases = ["m"])
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx: commands.Context, user: discord.Member, duration="", *, reason=""):
        """Mute a user. Example of duration 5m = 5 minutes"""
        with Session(engine) as session:
            mute_role = session.query(GuildData.mute_role_id).filter(GuildData.guild_id == ctx.message.guild.id).scalar()
            role = ctx.guild.get_role(int(mute_role))

        try:
            time = humanfriendly.parse_timespan(duration)
        except humanfriendly.InvalidTimespan:
            print("invalid timespand")
            reason = duration + " " + reason

            await Admin.add_punishment(user.id, ctx.message.author.id, ctx.message.guild.id, "Mute", reason, "Perma")

            await user.add_roles(role)

            return await ctx.reply(f"{user} has been muted for **unlimited time**. Reason: **{reason}**")

        await Admin.add_punishment(user.id, ctx.message.author.id, ctx.message.guild.id, "Mute", reason, humanfriendly.format_timespan(time))
        
        await ctx.reply(f"{user} has been muted for **{humanfriendly.format_timespan(time)}**. Reason: **{reason}**")
        await user.add_roles(role)
        await asyncio.sleep(time)
        await user.remove_roles(role)
        await ctx.send(f"{user} has been unmuted")
        

    @commands.command(aliases = ["um"])
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, ctx: commands.Context, user: discord.Member):
        """Unmute a user"""
        with Session(engine) as session:
            mute_role = session.query(GuildData.mute_role_id).filter(GuildData.guild_id == ctx.message.guild.id).scalar()
            role = ctx.guild.get_role(int(mute_role))

        await user.remove_roles(role)
        await ctx.send(f"{user} has been unmuted") 

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def warn(self, ctx: commands.Context, user: discord.Member, perma: bool, *, reason):
        """warn a user. Perma: True/False"""
        current_time = datetime.utcnow()
        with Session(engine) as session:
            add_warn = Warning(
                reason=reason,
                warned_user_id=user.id,
                warned_by_user_id=ctx.author.id,
                warn_date = current_time,
                expire_date = current_time + timedelta(seconds=session.query(GuildData.warn_length).filter(GuildData.guild_id == ctx.message.guild.id).scalar()),
                perma = perma,
                guild_id = ctx.message.guild.id
            )
            session.add(add_warn)
            session.commit()
        
        await ctx.reply("User has been warned")
    
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def warns(self, ctx: commands.Context, user: discord.Member):
        """See the warns of a user"""
        with Session(engine) as session:
            warns = session.query(Warning).filter(and_(Warning.warned_user_id == user.id, Warning.guild_id == ctx.message.guild.id)).all()
        
        embed = discord.Embed(title=f"Warns for user {user.display_name}#{user.discriminator}", description=f"User ID: {user.id}")
        for warn in warns:
            exp = str(warn.expire_date)[:-7]
            if warn.perma is True:
                exp = "Never"
            embed.add_field(name=f"Warn ID: {warn.id}", value=f"\"{warn.reason}\" \n \n**Warned by:** {ctx.guild.get_member(warn.warned_by_user_id)} \n**Warned:** {str(warn.warn_date)[:-7]} \n**Expires:** {exp}", inline=False)
        
        await ctx.reply(embed=embed)
    
    @commands.command(aliases = ["pun", "punish"])
    @commands.has_permissions(manage_messages=True)
    async def punishments(self, ctx: commands.Context, user: discord.Member):
        """Check a users punishments"""
        with Session(engine) as session:
            p = session.query(GuildUserPunishment).filter(and_(GuildUserPunishment.user_id == user.id, GuildUserPunishment.guild_id == ctx.message.guild.id)).all()
        
        embed = discord.Embed(title=f"Punishments for user {user}", description=f"User ID: {user.id}")
        for punish in p:
            embed.add_field(name=f"{punish.type}", value=f"**Reason:** {punish.reason} \n \n**Punished by:** {ctx.guild.get_member(punish.punisher_id)} \n**Date:** {str(punish.punish_date)[:-7]} \n**Duration:** {punish.duration}", inline=False)

        await ctx.reply(embed=embed)

    @commands.command(aliases = ["delwarn", "dw"])
    @commands.has_permissions(manage_roles=True)
    async def deletewarn(self, ctx: commands.Context, warn_id):
        """Delete warn"""
        with Session(engine) as session:
            session.query(Warning).filter(and_(Warning.id == warn_id, Warning.guild_id == ctx.message.guild.id)).delete()
            session.commit()
        await ctx.reply("Warn deleted")

    @commands.command(aliases = ["delmsg"])
    @commands.has_permissions(view_audit_log=True)
    async def delmessagelog(self, ctx: commands.Context):
        """Logs of deleted messages"""
        with Session(engine) as session:
            msgs = session.query(DelMessageLog).filter(DelMessageLog.guild_id == ctx.message.guild.id)
        fmsg = "All deleted messages for server:"
        for msg in msgs:
            fmsg = fmsg + f"\n \n\"{msg.content}\" \nFrom {ctx.guild.get_member(msg.user_id)} in {ctx.guild.get_channel(msg.channel_id)} \n{str(msg.del_time)[:-7]}"
        await ctx.reply(fmsg)


    @commands.command()
    @commands.has_permissions(view_audit_log=True)
    async def purge(self, ctx: commands.Context, purge_limit):
        """Purge a specific amount of messages"""
        try:
            await ctx.message.delete()
            purge_limit = int(purge_limit)
        except ValueError:
            return await ctx.reply("Not a valid limit")

        deleted = await ctx.channel.purge(limit = purge_limit)
        await ctx.send(f"Deleted {len(deleted)} message(s)")

def setup(bot: commands.Bot):
    bot.add_cog(Admin(bot))
