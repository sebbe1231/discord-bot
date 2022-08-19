import discord
from discord.ext import commands
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from database import DelMessageLog, GuildData, engine
import humanfriendly
from helpers import db
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger

class Admin(commands.Cog):
    """Commands for admin and admin like perms only"""
    def __init__(self, bot):
        self.bot = bot
        self.emoji = ":shield:"
        self.schedualar = AsyncIOScheduler(event_loop=bot.loop)
        self.schedualar.start()

    @staticmethod
    async def user_unmute(bot, user_id, guild_id, date, length):
        if db.get_user_relation(user_id, guild_id).mute_date == date and db.get_user_relation(user_id, guild_id).mute_length == length:
            with Session(engine) as session:
                db.get_user_relation(user_id, guild_id).remove_mute()

                mute_role = session.query(GuildData.mute_role_id).filter(GuildData.guild_id == guild_id).scalar()
                await bot.get_guild(guild_id).get_member(user_id).remove_roles(bot.get_guild(guild_id).get_role(int(mute_role)))

                if db.get_guild_data(guild_id).bot_audit_id:
                    channel = bot.get_guild(guild_id).get_channel(db.get_guild_data(guild_id).bot_audit_id)
                    await channel.send(f"```{bot.get_user(user_id)} ({user_id}) has been unmuted```")

    @staticmethod
    async def user_unban(bot, user_id, guild_id, date, length):
        if db.get_user_relation(user_id, guild_id).ban_date == date and db.get_user_relation(user_id, guild_id).ban_length == length:
            db.get_user_relation(user_id, guild_id).remove_mute()

            await bot.get_guild(guild_id).unban(bot.get_guild(guild_id).get_member(user_id))

            if db.get_guild_data(guild_id).bot_audit_id:
                channel = bot.get_guild(guild_id).get_channel(db.get_guild_data(guild_id).bot_audit_id)
                await channel.send(f"```{bot.get_user(user_id)} ({user_id}) has been unbanned```")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, user: discord.Member, duration=None, *, reason=None):
        """Ban a user. Example of duration 5m = 5 minutes"""
        date = datetime.utcnow()
        try:
            time = humanfriendly.parse_timespan(duration)
        except humanfriendly.InvalidTimespan:
            reason = duration + " " + reason
            
            #Actual banning process
            db.get_user_relation(user.id, ctx.guild.id).add_ban(date, -1)
            await ctx.guild.ban(user, reason=reason)
            await ctx.reply(f"{user} has been banned for **unlimited time**. Reason: **{reason}**")

            # bot audit
            if db.get_guild_data(ctx.guild.id).bot_audit_id:
                channel = ctx.guild.get_channel(db.get_guild_data(ctx.guild.id).bot_audit_id)
                await channel.send(
                    f"""```{ctx.author} ({ctx.author.id}) has banned {user} 
                        ({user.id}) for unlimited time due to \"{reason}\"```"""
                    )

            return

        # Actual banning process
        db.get_user_relation(user.id, ctx.guild.id).add_ban(date, time)
        await ctx.guild.ban(user, reason=reason)

        await ctx.reply(f"{user} has been banned for **{humanfriendly.format_timespan(time)}**. Reason: **{reason}**")

        # bot audit
        if db.get_guild_data(ctx.guild.id).bot_audit_id:
            channel = ctx.guild.get_channel(db.get_guild_data(ctx.guild.id).bot_audit_id)
            await channel.send(
                f"""```{ctx.author} ({ctx.author.id}) has banned {user} ({user.id}) 
                    for {humanfriendly.format_timespan(time)} due to \"{reason}\"```"""
                )
        
        self.schedualar.add_job(Admin.user_unmute, DateTrigger(date+timedelta(seconds=time), timezone=timezone.utc), (self.bot, user.id, ctx.guild.id, date, time))
    
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx: commands.Context, user: discord.User):
        """Unban a user"""
        try:
            await ctx.guild.unban(user)
        except discord.errors.NotFound:
            return await ctx.reply("User is not banned")
        await ctx.reply(f"{user} has been unbanned")

        # bot audit
        if db.get_guild_data(ctx.guild.id).bot_audit_id:
            channel = ctx.guild.get_channel(db.get_guild_data(ctx.guild.id).bot_audit_id)
            await channel.send(f"```{ctx.author} ({ctx.author.id}) has unbanned {user} ({user.id})```")
    
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, user: discord.Member, *, reason=""):    
        await ctx.guild.kick(user, reason=reason)
        await ctx.send(f"{user} has been kicked. Reason: **{reason}**")

        # bot audit
        if db.get_guild_data(ctx.guild.id).bot_audit_id:
            channel = ctx.guild.get_channel(db.get_guild_data(ctx.guild.id).bot_audit_id)
            await channel.send(f"```{ctx.author} ({ctx.author.id}) has kicked {user} ({user.id}) due to \"{reason}\"```")

    @commands.command(aliases = ["m"])
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx: commands.Context, user: discord.Member, duration="", *, reason=""):
        """Mute a user. Example of duration 5m = 5 minutes"""
        date = datetime.utcnow()
        with Session(engine) as session:
            mute_role = session.query(GuildData.mute_role_id).filter(GuildData.guild_id == ctx.message.guild.id).scalar()
            try:
                role = ctx.guild.get_role(int(mute_role))
            except TypeError:
                return await ctx.reply(f"No mute role added to database. To add this do `{ctx.prefix}muterole <mute_id>`")

        try:
            time = humanfriendly.parse_timespan(duration)
        except humanfriendly.InvalidTimespan:
            print("invalid timespand")
            reason = duration + " " + reason

            await user.add_roles(role)
            await ctx.reply(f"{user} has been muted for **unlimited time**. Reason: **{reason}**")

            db.get_user_relation(user.id, ctx.guild.id).remove_mute()
            db.get_user_relation(user.id, ctx.guild.id).add_mute(date, -1)

            # bot audit
            if db.get_guild_data(ctx.guild.id).bot_audit_id:
                channel = ctx.guild.get_channel(db.get_guild_data(ctx.guild.id).bot_audit_id)
                await channel.send(
                    f"""```{ctx.author} ({ctx.author.id}) has muted {user} 
                        ({user.id}) for unlimited time due to \"{reason}\"```"""
                    )
            return
        
        db.get_user_relation(user.id, ctx.guild.id).remove_mute()
        db.get_user_relation(user.id, ctx.guild.id).add_mute(date, time)
        
        await user.add_roles(role)

        await ctx.reply(f"{user} has been muted for **{humanfriendly.format_timespan(time)}**. Reason: **{reason}**")
        
        # bot audit
        if db.get_guild_data(ctx.guild.id).bot_audit_id:
            channel = ctx.guild.get_channel(db.get_guild_data(ctx.guild.id).bot_audit_id)
            await channel.send(f"```{ctx.author} ({ctx.author.id}) has muted {user} ({user.id}) for {humanfriendly.format_timespan(time)} due to \"{reason}\"```")
        
        self.schedualar.add_job(Admin.user_unmute, DateTrigger(date+timedelta(seconds=time), timezone=timezone.utc), (self.bot, user.id, ctx.guild.id, date, time))
        

    @commands.command(aliases = ["um"])
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, ctx: commands.Context, user: discord.Member):
        """Unmute a user"""
        mute_role = db.get_guild_data(ctx.guild.id).mute_role_id
        role = ctx.guild.get_role(int(mute_role))

        await user.remove_roles(role)
        db.get_user_relation(user.id, ctx.guild.id).remove_mute()

        await ctx.reply(f"{user} has been unmuted")

        # bot audit
        if db.get_guild_data(ctx.guild.id).bot_audit_id:
            channel = ctx.guild.get_channel(db.get_guild_data(ctx.guild.id).bot_audit_id)
            await channel.send(f"```{ctx.author} ({ctx.author.id}) has unmuted {user} ({user.id})```") 

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def warn(self, ctx: commands.Context, user: discord.Member, perma: bool, *, reason):
        """warn a user. Perma: True/False"""
        db.add_warn(reason, user.id, ctx.author.id, perma, ctx.guild.id)
        
        await ctx.reply("User has been warned")

        #bot audit
        if db.get_guild_data(ctx.guild.id).bot_audit_id:
            channel = ctx.guild.get_channel(db.get_guild_data(ctx.guild.id).bot_audit_id)
            await channel.send(f"```{ctx.author} ({ctx.author.id}) has warned {user} ({user.id}) due to \"{reason}\"```")
    
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def warns(self, ctx: commands.Context, user: discord.Member):
        """See the warns of a user"""
        embed = discord.Embed(title=f"Warns for user {user.display_name}#{user.discriminator}", description=f"User ID: {user.id}")
        for warn in db.get_user_warns(user.id, ctx.guild.id):
            exp = str(warn.expire_date)[:-7]
            if warn.perma is True:
                exp = "Never"
            embed.add_field(name=f"Warn ID: {warn.id}", 
                value=f"""\"{warn.reason}\" \n \n**Warned by:** 
                {ctx.guild.get_member(warn.warned_by_user_id)} \n**Warned:** {str(warn.warn_date)[:-7]} 
                \n**Expires:** {exp}""", inline=False
            )
        
        await ctx.reply(embed=embed)

    @commands.command(aliases = ["delwarn", "dw"])
    @commands.has_permissions(manage_roles=True)
    async def deletewarn(self, ctx: commands.Context, warn_id):
        """Delete warn"""
        db.delete_warn(warn_id)
        await ctx.reply("Warn deleted")

        # bot audit
        if db.get_guild_data(ctx.guild.id).bot_audit_id:
            channel = ctx.guild.get_channel(db.get_guild_data(ctx.guild.id).bot_audit_id)
            await channel.send(f"```{ctx.author.id} ({ctx.author.id}) deleted a warn```")

    @commands.command(aliases = ["delmsg"])
    @commands.has_permissions(view_audit_log=True)
    async def delmessagelog(self, ctx: commands.Context):
        """Logs of deleted messages"""
        with Session(engine) as session:
            msgs = session.query(DelMessageLog).filter(DelMessageLog.guild_id == ctx.message.guild.id)
        fmsg = "All deleted messages for server:"
        for msg in msgs:
            if len(fmsg) + len(f"""\n \n\"{msg.content}\" 
                \nFrom {ctx.guild.get_member(msg.user_id)} in #{ctx.guild.get_channel(msg.channel_id)} 
                \n{str(msg.del_time)[:-7]}"""
            ) > 2000:
                await ctx.reply(f"```{fmsg}```")
                fmsg = ""
            else:
                fmsg = fmsg + f"""\n \n\"{msg.content}\" \nFrom {ctx.guild.get_member(msg.user_id)} 
                    in #{ctx.guild.get_channel(msg.channel_id)} \n{str(msg.del_time)[:-7]}"""
        await ctx.reply(f"```{fmsg}```")


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

        # bot audit
        if db.get_guild_data(ctx.guild.id).bot_audit_id:
            channel = ctx.guild.get_channel(db.get_guild_data(ctx.guild.id).bot_audit_id)
            await channel.send(f"```{ctx.author} ({ctx.author.id}) purged {purge_limit} message(s) in #{ctx.channel}```")

def setup(bot: commands.Bot):
    bot.add_cog(Admin(bot))
