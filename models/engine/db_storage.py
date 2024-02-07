"""handles db storage"""
import models
from models.user import User
from models.game import Game
from models.base_model import Base, BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


classes = {
    'User': User,
    'Game': Game
}

class DbStorage():
    """represents the db storge model"""

    __engine = ""
    __session = ""

    def __init__(self):

        self.__engine = create_engine('mysql+pymysql://root:sunesis@localhost/chess_game')

    def all(self, cls=None):
        """gets all data for a class"""
        new_dict = {}
        if cls is None:
            for clss in classes:
                objs = self.__session.query(classes[clss]).all()
                for obj in objs:
                    key = obj.__class__.__name__ + '.' + obj.id
                    new_dict[key] = obj
        else:
            objs = self.__session.query(cls).all()
            for obj in objs:
                key = obj.__class__.__name__ + '.' + obj.id
                new_dict[key] = obj
        return new_dict
    
    def new(self, obj):
        """creates new instance"""
        self.__session.add(obj)

    def save(self):
        """saves a session"""
        self.__session.commit()
    
    def delete(self, obj):
        """deletes an object"""
        if obj is not None:
            self.__session.delete(obj)

    def reload(self):
        """reload"""
        Base.metadata.create_all(self.__engine)
        sess_factory = sessionmaker(bind=self.__engine, expire_on_commit=False)
        Session = scoped_session(sess_factory)
        self.__session = Session

    def close(self):
        self.__session.remove()

    def get(self, cls, id):
        return self.__session.query(cls).get(id)
        
    def get_google_id(self, cls, id):
        if cls == User:
            return self.__session.query(cls).filter(cls.google_id == id).first()
    def count(self, cls=None):
        """count ojects in a cls in storage."""
        objs = self.all(cls)
        return len(objs)
            

    