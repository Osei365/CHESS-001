"""the Game model"""

from models.base_model import Base, BaseModel
from sqlalchemy import Column, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression


class Game(BaseModel, Base):
    __tablename__ = 'games'
    opponent = Column(String(60), nullable=True)
    opponent_name = Column(String(60), nullable=True)
    game_style = Column(String(60), nullable=True)
    user_start = Column(Boolean, default=True, server_default=expression.true())
    engine = Column(String(60), nullable=True)
    user_id = Column(String(60), ForeignKey('users.id'), nullable=False)