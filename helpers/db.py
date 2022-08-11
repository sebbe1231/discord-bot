import database
from typing import Union
from sqlalchemy.orm import Session
from sqlalchemy import and_
with Session(database.engine) as session:
    def get_user(discord_id: int) -> database.User:
        user = session.query(database.User).filter(database.User.user_id == discord_id).first()
        return user
    
    def get_user_relation(user, guild_id: int) -> database.UserRelations:
        user = get_user(user)
        for data in user.user_relations:
            if data.guild_id == guild_id:
                print(data.guild_id, data.coins)
                data.coins = data.coins - 1
                print(data.guild_id, data.coins)
        
        