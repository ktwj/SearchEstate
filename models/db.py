from sqlalchemy import *
from sqlalchemy import Column, Integer, VARCHAR, DateTime, TEXT
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
import datetime, hashlib, psycopg2
from flask import session as ss
from pysrc import env

database = env.APP_database
user = env.APP_user
password = env.APP_password
host = env.APP_host
port = env.APP_port

uri = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'

engine = create_engine(uri,echo=True)

session = scoped_session(
    sessionmaker(
        autoflush = False,
        autocommit = False,
        bind = engine,
    )
)

def hashed(name,p,n):
    for _ in range(n):
        p = hashlib.sha256(bytes(name+p+name, 'utf-8')).hexdigest()
    return p

db = declarative_base()
db.query = session.query_property()

class Users(db):
    __tablename__ = 'users'
    id = Column(Integer(), primary_key=True)
    name = Column(VARCHAR(32))
    password = Column(VARCHAR(64))
    deleted_at = Column(DateTime())
    fbid = Column(TEXT())
    def __init__(self, name, words, types):
        print('0')
        self.name = name
        print('1')
        if types == 'fb':
            self.fbid = words
        elif types == 'normal':
            self.password = hashed(name,words,100)
        else:
            self.password = hashed(name,words,100)
    def __repr__(self):
        return f'Users {self.id} / {self.name} / {self.password}'

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
        return 'UserID:{0},\n{1}'.format(self.user_id, self.title)

def add_user(user):
    if (user.name==null) or (user.password==null):
        print('3')
        return '??????????????????????????????????????????????????????'
    else:
        if user.fbid == null:
            print('4')
            session.add(user)
            session.commit()
            return '??????????????????'
        else:
            if session.query(Users).filter(Users.fbid==user.fbid).first():
                return '??????FB????????????????????????????????????????????????'
            else:
                session.add(user)
                session.commit()
                return 'FB????????????????????????????????????'

def check_user(name,password):
    user = session.query(Users).filter(Users.name==name).filter(Users.password==hashed(name,password,100)).first()
    return user

def check_fb_user(fbid):
    user = session.query(Users).filter(Users.fbid==fbid).first()
    return user

def add_fbid(id, fbid):
    if session.query(Users).filter(Users.fbid==fbid).first():
        return '??????FB????????????????????????????????????????????????'
    else:
        user = session.query(Users).filter(Users.id==id).first()
        user.fbid = fbid
        session.commit()
        return 'FB????????????????????????????????????'

def add_room(room):
    session.add(room)
    session.commit()

def del_room(ids):
    for id in ids:
        room = session.query(Rooms).filter(Rooms.user_id==ss['id']).filter(Rooms.id==id).first()
        room.deleted_at = datetime.datetime.now()
    session.commit()

def del_all_list():
    session.query(search_list).delete()
    session.commit()
    session.close()

def list_of_rooms(user_id):
    rooms = session.query(Rooms).filter(Rooms.user_id==user_id).filter(or_(Rooms.deleted_at==None, Rooms.deleted_at=="2021-01-01 00:00:00")).all()
    return rooms

"""
Session = sessionmaker(bind=engine)
db_session = Session()
db.metadata.create_all(engine)
"""