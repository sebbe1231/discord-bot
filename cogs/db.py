from select import select
import string
from time import timezone
import discord
from discord.ext import commands,tasks
import sqlite3
from datetime import datetime, timedelta, tzinfo

class Db(commands.Cog):
    def __init__ (self, bot: commands.Bot):
        self.bot = bot
        #self.check_warns.start()
    
    # @commands.Cog.listener()
    # async def on_guild_join(guild):
    #     print(f"Bot init on guild join: {guild}: \t{guild.id}")
    #     conn = sqlite3.connect(f"./cogs/db_strg/{guild.id}.db")
    #     c = conn.cursor()

    #     c.execute("""CREATE TABLE IF NOT EXISTS warns (user_id integer, date text, warner_id integer, reason text, expire_date text, perma int)""")
    #     c.execute("""CREATE TABLE IF NOT EXISTS chat_logs (channel_id integer, user_id integer, content text, date real)""")
    #     c.execute("""CREATE TABLE IF NOT EXISTS prefix (prefix)""")

    #     c.execute("""SELECT * FROM prefix""")
    #     res = c.fetchone()

    #     if not res:
    #         c.execute("""INSERT INTO prefix VALUES ('.')""")

    #     conn.commit()
    #     conn.close()

    # @commands.Cog.listener()
    # async def on_ready(self):
    #     for guild in self.bot.guilds:
    #         print(f"First check on startup: {guild}: \t{guild.id}")
    #         conn = sqlite3.connect(f"./cogs/db_strg/{guild.id}.db")
    #         c = conn.cursor()

    #         c.execute("""CREATE TABLE IF NOT EXISTS warns (user_id integer, date text, warner_id integer, reason text, expire_date text, perma text)""")
    #         c.execute("""CREATE TABLE IF NOT EXISTS chat_logs (channel_id integer, user_id integer, content text, date real)""")
    #         c.execute("""CREATE TABLE IF NOT EXISTS prefix (prefix text)""")
    #         c.execute("""CREATE TABLE IF NOT EXISTS perms (role_id integer, banperms text, kickperms text, warnperms text, muteperms text, purgeperms text)""")

    #         c.execute("""SELECT * FROM prefix""")
    #         res = c.fetchone()

    #         if not res:
    #             c.execute("""INSERT INTO prefix VALUES ('.')""")

    #         conn.commit()
    #         conn.close()

    # @tasks.loop(minutes=1.0)
    # async def check_warns(self):
    #     print(f"Looking through warns...: \t{datetime.utcnow()}")
    #     for database in self.bot.guilds:
    #         conn = sqlite3.connect(f"./cogs/db_strg/{database.id}.db")
    #         c = conn.cursor()

    #         del_id = []

    #         for row in c.execute("""SELECT rowid, * FROM warns"""):
    #             if row[6] == 0:
    #                 date_of_expire = datetime.strptime(row[5], "%Y-%m-%d %H:%M:%S")
    #                 if date_of_expire < datetime.utcnow():
    #                     print(f"WARN IS EXPIRED: \nID: {row[0]} \tUSER: {row[1]} \nDATE: {row[2]} \t{row[5]}, \nCURRENT TIME: {datetime.utcnow()}")
    #                     del_id.append(row[0])
    #                 else:
    #                     print("No more warns to delete")
    #                     break
    #         for id in del_id:
    #             c.execute(f"""DELETE FROM warns WHERE rowid = {id}""")
    #             print("Warn deleted successfully")
    #     conn.commit()
    #     conn.close()
    
    # @check_warns.before_loop
    # async def check_warns_before(self):
    #     await self.bot.wait_until_ready()

                


    
    # @commands.Cog.listener()
    # async def on_message_delete(self, message):
    #     conn = sqlite3.connect(f"./cogs/db_strg/{message.guild.id}.db")
    #     c = conn.cursor()

    #     c.execute(f"INSERT INTO chat_logs VALUES ({message.channel.id}, {message.author.id}, '{message.content}', 0)")

    #     conn.commit()
    #     conn.close()
        
        


def setup(bot: commands.Bot):
    bot.add_cog(Db(bot))