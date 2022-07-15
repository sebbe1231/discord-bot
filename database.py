#from curses import echo
from datetime import datetime
from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Index, Integer, String, DateTime, Text, UniqueConstraint, create_engine, true
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from os import environ

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True)
    user_id = Column(BigInteger)
    registered = Column(DateTime())

    warnings = relationship("Warning", backref="users")
    del_logs = relationship("DelMessageLog", backref="users")
    bans = relationship("GuildUserPunishment", backref="users")

    UniqueConstraint(user_id)

    def __repr__(self):
        return f"User(id={self.id!r}, user_id={self.user_id!r}, username={self.username!r})"

class Warning(Base):
    __tablename__ = "warnings"

    id = Column(Integer, primary_key = True)
    reason = Column(String)
    warned_user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable = False)
    warned_by_user_id = Column(BigInteger)
    warn_date = Column(DateTime)
    expire_date = Column(DateTime)
    perma = Column(Boolean)
    guild_id = Column(BigInteger)

    def __repr__(self):
        return f"Warning(id={self.id!r}, reason={self.reason!r}, warned_user_id={self.warned_user_id!r}, warned_by_user_id={self.warned_by_user_id!r})"

class GuildData(Base):
    __tablename__ = "guilddata"

    id = Column(Integer, primary_key = True)
    guild_id = Column(BigInteger)
    bot_prefix = Column(String)
    mute_role_id = Column(BigInteger)
    warn_length = Column(BigInteger)
    date_modified = Column(DateTime, onupdate=datetime.utcnow())

    bans = relationship("GuildUserPunishment", backref="guilddata")

    UniqueConstraint(guild_id)

class DelMessageLog(Base):
    __tablename__="delmessagelogs"

    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger)
    channel_id = Column(BigInteger)
    user_id = Column(BigInteger, ForeignKey("users.user_id"))
    content = Column(Text)
    del_time = Column(DateTime())

class GuildUserPunishment(Base):
    __tablename__="guilduserpunishments"

    id = Column(Integer, primary_key = True)
    guild_id = Column(BigInteger, ForeignKey("guilddata.guild_id"))
    user_id = Column(BigInteger, ForeignKey("users.user_id"))
    punisher_id = Column(BigInteger)
    type = Column(String)
    reason = Column(Text)
    duration = Column(String)
    punish_date = Column(DateTime)









engine = create_engine(environ['DB_KEY'], echo=False, future=true)
Base.metadata.create_all(engine)