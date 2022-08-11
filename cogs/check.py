from discord.ext import commands,tasks
from datetime import datetime
from sqlalchemy.orm import Session
from database import DelMessageLog, GuildData, User, GuildData, Warning, UserRelations, engine
from sqlalchemy import and_, func, inspect, select

class Check(commands.Cog):
    def __init__ (self, bot: commands.Bot):
        self.bot = bot
        self.check_warns.start()

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
    
    @commands.Cog.listener()
    async def on_ready(self):
        with Session(engine) as session:
            for guild in self.bot.guilds:
                data = session.query(GuildData).filter_by(guild_id = guild.id).first() is not None
                if not data:
                    add_guild = GuildData(
                        guild_id = guild.id,
                        bot_prefix = ".",
                        date_modified = datetime.utcnow(),
                        warn_length = 2630000
                    )
                    session.add(add_guild)
                    session.commit()
            
            i = 0
            for guild in self.bot.guilds:
                for member in guild.members:
                    data = session.query(User).filter(User.user_id == member.id).first() is not None
                    if not data:
                        i = i+1
                        add_user = User(
                            user_id = member.id,
                            registered = datetime.utcnow()
                        )
                        session.add(add_user)
                        session.commit()
                    
                    data = session.query(UserRelations).filter(and_(UserRelations.user_id == member.id, UserRelations.guild_id == guild.id)).first() is not None
                    if not data:
                        add_user = UserRelations(
                            user_id = member.id,
                            guild_id = guild.id
                        )
                        session.add(add_user)
                        session.commit()
            print(f"Added {i} users...")
                    
                        
    
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
    bot.add_cog(Check(bot))