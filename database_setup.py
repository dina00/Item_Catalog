import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from flask_login import UserMixin

Base = declarative_base()


class Users(Base, UserMixin):
    __tablename__ = 'users'
    # The id is of type string because,
    # Google returns the user's id as string.
    id = Column(String, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

    # Flask-Login integration
    def __init__(self, id, name, email, picture):
        self.id = id
        self.name = name
        self.email = email
        self.picture = picture

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '<User %r>' % (self.name)


class Categories(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class Items(Base):
    __tablename__ = 'items'
    # same thing here to use the user id it has to of type string.
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    categories = relationship(Categories)
    users = relationship(Users)
    cat_id = Column(Integer, ForeignKey('categories.id'))
    user_id = Column(String, ForeignKey('users.id'))


# To send JSON objects in a serializable format
    @property
    def serialize(self):

        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,

        }

    
engine = create_engine('sqlite:///catalog.db',
                       connect_args={'check_same_thread': False})


Base.metadata.create_all(engine)
