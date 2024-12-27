from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    phone_number = Column(String)

def init_db():
    engine = create_engine('sqlite:///users.db')  
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()