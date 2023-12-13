"""the Game model"""

from models.base_model import Base, BaseModel
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship


class Game(BaseModel, Base):
    __tablename__ = 'games'
    user_id = Column(String(60), ForeignKey('users.id'), nullable=False)