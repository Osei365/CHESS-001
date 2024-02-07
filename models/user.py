"""the User model"""

import models
from models.base_model import Base, BaseModel
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from flask_login import UserMixin



class User(BaseModel, Base, UserMixin):
    __tablename__ = 'users'
    google_id = Column(String(128), nullable=True, unique=True)
    email = Column(String(128), nullable=False)
    password = Column(String(128), nullable=True)
    users_name = Column(String(128), nullable=True)
    picture = Column(String(128), nullable=True)
    games = relationship("Game", backref="user")

    @staticmethod
    def get(id):
        models.storage.get(User, id)