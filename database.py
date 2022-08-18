#from curses import echo
from datetime import datetime, timedelta
from email.policy import default
from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Index, Integer, String, DateTime, Text, UniqueConstraint, create_engine, true, and_
from sqlalchemy.orm import declarative_base, relationship, Session
from sqlalchemy.sql import func
from os import environ

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True)
    user_id = Column(BigInteger)
    registered = Column(DateTime(), default=datetime.utcnow())

    warnings = relationship("Warning", backref="users")
    del_logs = relationship("DelMessageLog", backref="users")
    user_relations = relationship("UserRelations", backref="users")

    UniqueConstraint(user_id)

    def __repr__(self):
        return f"User(id={self.id!r}, user_id={self.user_id!r}, username={self.username!r})"

class Warning(Base):
    __tablename__ = "warnings"

    id = Column(Integer, primary_key = True)
    reason = Column(String)
    warned_user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable = False)
    warned_by_user_id = Column(BigInteger)
    warn_date = Column(DateTime, default=datetime.utcnow())
    expire_date = Column(DateTime)
    perma = Column(Boolean)
    guild_id = Column(BigInteger)

    def __repr__(self):
        return f"Warning(id={self.id!r}, reason={self.reason!r}, warned_user_id={self.warned_user_id!r}, warned_by_user_id={self.warned_by_user_id!r})"

class GuildData(Base):
    __tablename__ = "guilddata"

    id = Column(Integer, primary_key = True)
    guild_id = Column(BigInteger)
    bot_prefix = Column(String, default=".")
    mute_role_id = Column(BigInteger)
    warn_length = Column(BigInteger, default = 2630000)
    date_modified = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow())
    bot_audit_id = Column(BigInteger)

    user_relations = relationship("UserRelations", backref="guilddata")

    UniqueConstraint(guild_id)

class DelMessageLog(Base):
    __tablename__="delmessagelogs"

    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger)
    channel_id = Column(BigInteger)
    user_id = Column(BigInteger, ForeignKey("users.user_id"))
    content = Column(Text)
    del_time = Column(DateTime())

class UserRelations(Base):
    __tablename__="userrelations"

    id = Column(Integer, primary_key = True)
    user_id = Column(BigInteger, ForeignKey("users.user_id"))
    guild_id = Column(BigInteger, ForeignKey("guilddata.guild_id"))
    mute_date = Column(DateTime())
    mute_length = Column(BigInteger)
    ban_date = Column(DateTime())
    ban_length = Column(BigInteger)
    coins = Column(Integer, default=100)

    def set_coins(self, amount: int):
        with Session(engine) as session:
            relation = session.query(UserRelations).get(self.id)
            relation.coins = amount
            session.commit()
    
    def remove_mute(self):
        with Session(engine) as session:
            relation = session.query(UserRelations).get(self.id)
            relation.mute_date = None
            relation.mute_length = None
            session.commit()
    
    def add_mute(self, date: datetime, length: int):
        with Session(engine) as session:
            relation = session.query(UserRelations).get(self.id)
            relation.mute_date = date
            relation.mute_length = length
            session.commit()
    
    def remove_ban(self):
        with Session(engine) as session:
            relation = session.query(UserRelations).get(self.id)
            relation.ban_date = None
            relation.ban_length = None
            session.commit()
    
    def add_ban(self, date: datetime, length: int):
        with Session(engine) as session:
            relation = session.query(UserRelations).get(self.id)
            relation.ban_date = date
            relation.ban_length = length
            session.commit()
    

engine = create_engine(environ['DB_KEY'], echo=False, future=true)
Base.metadata.create_all(engine)