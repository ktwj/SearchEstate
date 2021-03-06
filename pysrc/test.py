from sqlalchemy import *
from sqlalchemy import and_, or_, Column, Integer, VARCHAR, Float, DateTime, TEXT
from sqlalchemy.orm import *
from sqlalchemy.sql import text
from sqlalchemy.ext.declarative import declarative_base
import datetime
from flask import session as ss
from pysrc import env

database = env.APP_database
user = env.APP_user
password = env.APP_password
host = env.APP_host
port = env.APP_port

uri = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}?client_encoding=utf8'

engine = create_engine(uri,echo=True,encoding='utf-8')
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
    index = Column(Integer(), primary_key=True, index=True)
    bukken_num = Column(Integer())
    title = Column(VARCHAR(100))
    address = Column(VARCHAR(100))
    line1 = Column(VARCHAR(100))
    station1 = Column(VARCHAR(100))
    time1 = Column(Integer())
    line2 = Column(VARCHAR(100))
    station2 = Column(VARCHAR(100))
    time2 = Column(Float())
    line3 = Column(VARCHAR(100))
    station3 = Column(VARCHAR(100))
    time3 = Column(Float())
    price = Column(Float())
    rent = Column(Float())
    fee = Column(Float())
    deposit = Column(Float())
    key = Column(Float())
    room_type = Column(VARCHAR(10))
    room_size = Column(Float())
    url = Column(VARCHAR(100))

class fav_list(db):
    __tablename__ = "fav_list"
    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer())
    title = Column(VARCHAR(100))
    address = Column(VARCHAR(100))
    line1 = Column(VARCHAR(100))
    station1 = Column(VARCHAR(100))
    time1 = Column(Float())
    line2 = Column(VARCHAR(100))
    station2 = Column(VARCHAR(100))
    time2 = Column(Float())
    line3 = Column(VARCHAR(100))
    station3 = Column(VARCHAR(100))
    time3 = Column(Float())
    rent = Column(Float())
    fee = Column(Float())
    deposit = Column(Float())
    key = Column(Float())
    room_type = Column(VARCHAR(10))
    room_size = Column(Float())
    url = Column(VARCHAR(100))
    deleted_at = Column(DateTime())
    def __init__(self,user_id,title,address,line1,station1,time1,line2,station2,time2,line3,station3,time3,rent,fee,deposit,key,room_type,room_size,url):
        self.user_id = user_id
        self.title = title
        self.address = address
        self.line1 = line1
        self.station1 = station1
        self.time1 = int(time1)
        self.line2 = line2
        self.station2 = station2
        self.time2 = float(time2)
        self.line3 = line3
        self.statio3n = station3
        self.time3 = float(time3)
        self.rent = float(rent)
        self.fee = float(fee)
        self.deposit = float(deposit)
        self.key = float(key)
        self.room_type = room_type
        self.room_size = float(room_size)
        self.url = url

def searching(station, mins, minp, maxp, shikirei, room_size_min, room_size_max):
    #t = text(f"and_(or_(and_(search_list.station1.like('%{station}%'), search_list.time1 <= {mins}), and_(search_list.station2.like('%{station}%'), search_list.time2 <= {mins}), and_(search_list.station3.like('%{station}%'), search_list.time3 <= {mins})), {minp} <= search_list.price, search_list.price <= {maxp})")
    t = text(f"( (station1 like '%{station}%' and time1<={mins}) or (station2 like '%{station}%' and time2<={mins}) or (station3 like '%{station}%' and time3<={mins}) ) and {minp}<=price and price<={maxp} and deposit+key <= {shikirei} and room_size >= {room_size_min} and room_size <= {room_size_max}")
    bukkens = session.query(search_list).filter(t).all()
    session.close()
    return bukkens

def add_fav_room(room):
    session.add(room)
    session.commit()
    session.close()

def list_of_fav(user_id):
    rooms = session.query(fav_list).filter(fav_list.user_id==user_id).filter(fav_list.deleted_at==None).all()
    session.close()
    return rooms

def del_all_list():
    session.query(search_list).delete()
    session.commit()
    session.close()

def del_fav(ids,ss_id):
    for id in ids:
        room = session.query(fav_list).filter(fav_list.user_id==ss_id).filter(fav_list.id==id).first()
        room.deleted_at = datetime.datetime.now()
    session.commit()
    session.close()

