from sqlalchemy import *
from sqlalchemy import Column, Integer, VARCHAR, DateTime, TEXT
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
import datetime, hashlib, psycopg2
from flask import session as ss

database = 'pydb'
user = 'postgres'
password = 'pass'
host = 'localhost'
port = '5432'
db_name = 'pydb'

uri = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}'

engine = create_engine(uri,echo=True)

session = scoped_session(
    sessionmaker(
        autoflush = False,
        autocommit = False,
        bind = engine,
    )
)

db = declarative_base()
db.query = session.query_property()

class Rooms(db):
    __tablename__ = 'rooms'
    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer())
    title = Column(TEXT)
    near = Column(TEXT)
    cost = Column(TEXT)
    link = Column(TEXT)
    transfer = Column(TEXT)
    deleted_at = Column(DateTime())

    def __init__(self,user_id,title,near,cost,link,transfer):
        self.user_id=user_id
        self.title=title
        self.near=near
        self.cost=cost
        self.link=link
        self.transfer=transfer
    
    def __repr__(self):
        return f'UserID:{self.user_id},\n{self.title}\n{self.near}\n{self.transfer}'

def tester():
    rooms = session.query(Rooms).filter(Rooms.user_id==3).filter(Rooms.deleted_at==None).all()
    return rooms

for i in tester():
    print(i['near'])