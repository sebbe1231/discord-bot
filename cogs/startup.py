from discord.ext import commands,tasks
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import DelMessageLog, GuildData, User, GuildData, Warning, UserRelations, engine
from sqlalchemy import and_, func, inspect, select

import asyncio

class Startup(commands.Cog):
    def __init__ (self, bot: commands.Bot):
        self.bot = bot
        self.check_warns.start()

    async def continue_mute(user_id: int, guild_id: int, time:int):
        print(user_id)
        print(guild_id)
        print(time)
        await asyncio.sleep(2)


    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Bot startup process...")
        date = datetime.utcnow()
        with Session(engine) as session:
            for user in session.query(UserRelations).filter(and_(UserRelations.mute_date is not None, UserRelations.mute_length is not None)):
                if user.mute_length == -1 or user.mute_length is None:
                    continue
                exp = user.mute_date + timedelta(seconds=user.mute_length)
                if exp > datetime.utcnow():
                    loop = asyncio.get_event_loop()
                    try:
                        loop.run_until_complete(await Startup.continue_mute(user_id=user.user_id, guild_id=user.guild_id, time=exp.timestamp()-datetime.utcnow().timestamp()))
                    finally:
                        loop.close()
                elif exp <= datetime.utcnow():
                    mute_role = session.query(GuildData.mute_role_id).filter(GuildData.guild_id == user.guild_id).scalar()
                    await self.bot.get_guild(user.guild_id).get_member(user.user_id).remove_roles(self.bot.get_guild(user.guild_id).get_role(int(mute_role)))

                    user = session.query(UserRelations).filter(UserRelations.id == user.id).first()
                    user.mute_date = None
                    user.mute_length = None
            
            session.commit()
                    


                








    @commands.Cog.listener()
    async def on_guild_join(guild):
        print(f"Bot joined server: {guild}({guild.id})... Preparing server setup.")
        with Session(engine) as session:
            data = session.query(GuildData).filter_by(guild = guild.id).first() is not None
            if not data:
                add_guild = GuildData(
                    guild_id = guild.id,
                    bot_prefix = ".",
                    date_modified = datetime.utcnow()

                )
            session.add(add_guild)
            session.commit()
    
    # @commands.Cog.listener()
    # async def on_ready(self):
    #     with Session(engine) as session:
    #         for guild in self.bot.guilds:
    #             data = session.query(GuildData).filter_by(guild_id = guild.id).first() is not None
    #             if not data:
    #                 add_guild = GuildData(
    #                     guild_id = guild.id,
    #                     bot_prefix = ".",
    #                     date_modified = datetime.utcnow(),
    #                     warn_length = 2630000
    #                 )
    #                 session.add(add_guild)
    #                 session.commit()
            
    #         i = 0
    #         for guild in self.bot.guilds:
    #             for member in guild.members:
    #                 data = session.query(User).filter(User.user_id == member.id).first() is not None
    #                 if not data:
    #                     i = i+1
    #                     add_user = User(
    #                         user_id = member.id,
    #                         registered = datetime.utcnow()
    #                     )
    #                     session.add(add_user)
    #                     session.commit()
                    
    #                 data = session.query(UserRelations).filter(and_(UserRelations.user_id == member.id, UserRelations.guild_id == guild.id)).first() is not None
    #                 if not data:
    #                     add_user = UserRelations(
    #                         user_id = member.id,
    #                         guild_id = guild.id
    #                     )
    #                     session.add(add_user)
    #                     session.commit()
    #         print(f"Added {i} users...")
                    
                        
    
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