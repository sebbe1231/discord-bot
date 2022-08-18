from discord.ext import commands,tasks
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from database import DelMessageLog, GuildData, User, GuildData, Warning, UserRelations, engine
from sqlalchemy import and_, func, inspect, select
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from .admin import Admin

class Startup(commands.Cog):
    def __init__ (self, bot: commands.Bot):
        self.bot = bot
        self.check_warns.start()
        self.schedualar = AsyncIOScheduler(event_loop=bot.loop)
        self.schedualar.start()
        

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Bot startup process...")
        with Session(engine) as session:
            for user in session.query(UserRelations).filter(and_(UserRelations.mute_date is not None, UserRelations.mute_length is not None)):
                if user.mute_length == -1 or user.mute_length is None:
                    continue
                exp = user.mute_date + timedelta(seconds=user.mute_length)
                if exp > datetime.utcnow():
                    self.schedualar.add_job(Admin.user_unmute, DateTrigger(exp, timezone=timezone.utc), (self.bot, user.user_id, user.guild_id, user.mute_date, user.mute_length))
                elif exp <= datetime.utcnow():
                    await Admin.user_unmute(self.bot, user.user_id, user.guild_id, user.mute_date, user.mute_length)
            
            session.commit()

            for user in session.query(UserRelations).filter(and_(UserRelations.ban_date is not None, UserRelations.ban_length is not None)):
                if user.ban_length == -1 or user.ban_length is None:
                    continue
                exp = user.ban_date + timedelta(seconds=user.ban_length)
                if exp > datetime.utcnow():
                    self.schedualar.add_job(Admin.user_unban, DateTrigger(exp, timezone=timezone.utc), (self.bot, user.user_id, user.guild_id, user.ban_date, user.ban_length))
                elif exp <= datetime.utcnow():
                    await Admin.user_unban(self.bot, user.user_id, user.guild_id, user.ban_date, user.ban_length)
            
            session.commit()

            for guild in self.bot.guilds:
                data = session.query(GuildData).filter_by(guild_id = guild.id).first() is not None
                if not data:
                    if not data:
                        add_guild = GuildData(
                            guild_id = guild.id,
                        )
            session.add(add_guild)
            session.commit()


    @commands.Cog.listener()
    async def on_guild_join(guild):
        print(f"Bot joined server: {guild}({guild.id})... Preparing server setup.")
        with Session(engine) as session:
            data = session.query(GuildData).filter_by(guild = guild.id).first() is not None
            if not data:
                add_guild = GuildData(
                    guild_id = guild.id,
                )
            session.add(add_guild)
            session.commit()

    
        
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        with Session(engine) as session:
            add_message = DelMessageLog(
                guild_id = message.guild.id,
                channel_id = message.channel.id,
                user_id = message.author.id,
                content = message.content,
                del_time = datetime.utcnow()
            )
            session.add(add_message)
            session.commit()

    @tasks.loop(minutes=1.0)
    async def check_warns(self):
        print(f"Looking through warns...: \t{datetime.utcnow()}")
        with Session(engine) as session:
            print(f"Rows deleted: {session.query(Warning).filter(and_(Warning.expire_date <= datetime.utcnow(), Warning.perma == False)).delete()}")
            session.commit()
    
    @check_warns.before_loop
    async def check_warns_before(self):
        await self.bot.wait_until_ready()

def setup(bot: commands.Bot):
    bot.add_cog(Startup(bot))