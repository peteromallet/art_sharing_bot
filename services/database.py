from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy import create_engine, Column, Integer, String, Text, Table, MetaData
from sqlalchemy.orm import sessionmaker, registry, Session
from classes import User

# Setup SQLAlchemy engine and metadata
engine = create_engine('sqlite:///./database.db')
metadata = MetaData()

# Define the Users table
user_table = Table('users', metadata,
                   Column('id', Integer, primary_key=True, nullable=False),
                   Column('name', String),
                   Column('youtube_username', String),
                   Column('twitter_username', String),
                   Column('instagram_username', String),
                   Column('website_url', Text),
                   Column('featured', Boolean))

metadata.create_all(engine)

SESSION = sessionmaker(bind=engine)

# map class to table for ORM
mapper_registry = registry()
mapper_registry.map_imperatively(User, user_table)


def get_session():
    session = SESSION()
    return session


def insert_user(session: Session, user: User):
    session.add(user)
    session.commit()


def get_user(session: Session, user_id: int):
    result = session.query(user_table).filter_by(id=user_id).first()
    return result


def update_user(session: Session, user: User):
    # TODO: find a better way to do this
    user_dict = user.__dict__
    del user_dict['_sa_instance_state']
    session.query(user_table).filter_by(id=user.id).update(user_dict)
    session.commit()
