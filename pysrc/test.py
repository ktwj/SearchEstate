from sqlalchemy import *
from sqlalchemy import Column, Integer, VARCHAR, Float, DateTime, TEXT
from sqlalchemy.orm import *
from sqlalchemy.sql import text
from sqlalchemy.ext.declarative import declarative_base
import datetime, hashlib, psycopg2
from flask import session as ss

database = 'dgp2oe0v7u7ba'
user = 'fcjytqjkmrdcth'
password = 'd0d4acde298c07fedd9acf037ec024ffd15a8ee6ea2ea07876d8ab7dc840b256'
host = 'ec2-23-23-181-251.compute-1.amazonaws.com'
port = '5432'
db_name = 'pydb'

uri = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'

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

class search_list(db):
    __tablename__ = "search_list"
    col1 = Column(Integer(), primary_key=True, index=True)
    bukken_num = Column(Integer())
    title = Column(VARCHAR(100))
    address = Column(VARCHAR(100))
    line1 = Column(VARCHAR(100))
    station1 = Column(VARCHAR(100))
    time1 = Column(Integer())
    line2 = Column(VARCHAR(100))
    station2 = Column(VARCHAR(100))
    time2 = Column(Integer())
    line3 = Column(VARCHAR(100))
    station3 = Column(VARCHAR(100))
    time3 = Column(Integer())
    price = Column(Float())
    rent = Column(Float())
    fee = Column(Float())
    deposit = Column(Float())
    key = Column(Float())
    room_type = Column(VARCHAR(10))
    room_size = Column(Float())
    url = Column(VARCHAR(100))

def searching(station, mins, minp, maxp):
    t = text(f'(station1.str.contains("{station}")&time1<={mins} or station2.str.contains("{station}")&time2<={mins} station3.str.contains("{station}")&time3<={mins}) & {minp}<=price<={maxp}')
    bukkens = session.query(search_list).filter(t).all()
    return bukkens