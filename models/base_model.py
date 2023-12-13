"""base model that all other models inherit from"""

from models import storage
from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid



Base = declarative_base()

class BaseModel:
    """representation of base class"""
    id = Column(String(120), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.utcnow())

    def __init__(self, *args, **kwargs):
        if kwargs:
            for key, value in kwargs.items():
                setattr(self, key, value)

        self.id = str(uuid.uuid4())
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def save(self):
        """saves an instance of base model"""
        self.updated_at = datetime.utcnow()
        storage.new(self)
        storage.save()

    def delete(self):
        storage.delete(self)

            