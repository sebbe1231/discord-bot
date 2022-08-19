from database import engine, User, UserRelations, Warning, GuildData
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta

def get_user(discord_id: int) -> User:
    with Session(engine) as session:
        if not session.query(User).filter(User.user_id == discord_id).first():
            add_user = User(
                user_id = discord_id
            )
            session.add(add_user)
            session.commit()

        user = session.query(User).filter(User.user_id == discord_id).first()
        return user
        

def get_user_relation(user_id: int, guild_id: int) -> UserRelations:
    get_user(user_id)
    with Session(engine) as session:
        if session.query(UserRelations).filter(and_(UserRelations.user_id == user_id, UserRelations.guild_id == guild_id)).first() is None:
            add_relation = UserRelations(
                user_id = user_id,
                guild_id = guild_id
            )
            session.add(add_relation)
            session.commit()

        user_relation = session.query(UserRelations).filter(
            and_(UserRelations.user_id == user_id, UserRelations.guild_id == guild_id)
        ).first()
        
        return user_relation

def get_user_warns(user_id: int, guild_id: int) -> Warning:
    get_user(user_id)
    with Session(engine) as session:
        user_warns = session.query(Warning).filter(and_(Warning.warned_user_id == user_id, Warning.guild_id == guild_id)).all()

        return user_warns

def delete_warn(warn_id: int) -> None:
    with Session(engine) as session:
        session.query(Warning).filter(Warning.id == warn_id).delete()
        session.commit()
    
def add_warn(reason, user_id, warner_id, perma, guild_id) -> None:
    get_user(user_id)
    with Session(engine) as session:
        add_warn = Warning(
            reason=reason,
            warned_user_id=user_id,
            warned_by_user_id=warner_id,
            expire_date = datetime.utcnow() + timedelta(seconds=session.query(GuildData.warn_length).filter(GuildData.guild_id == guild_id).scalar()),
            perma = perma,
            guild_id = guild_id
        )
        session.add(add_warn)
        session.commit()

def get_guild_data(guild_id: int) -> GuildData:
    with Session(engine) as session:
        guild_data = session.query(GuildData).filter(GuildData.guild_id == guild_id).first()

        return guild_data