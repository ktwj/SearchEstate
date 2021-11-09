from sqlalchemy import *
from sqlalchemy import Column, Integer, VARCHAR, DateTime, TEXT
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
import datetime, hashlib, binascii
from flask import session as ss

uri = 'mysql+pymysql://{user}:{password}@{host}/{db_name}?charset=utf8'.format(**{
    'user': 'user',
    'password': 'pass',
    'host': 'localhost',
    'db_name': 'pydb'
})
engine = create_engine(uri,convert_unicode=True,echo=True)

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

class Posts(db):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    title = Column(TEXT)
    data = Column(TEXT)
    img = Column(TEXT)
    created_at = Column(DateTime())
    def __init__(self, title, data, img):
        self.title = title
        self.data = data
        self.img = img
    def __rept__(self):
        return 'Posts {} / {} / {}'.format(self.title,self.data,self.img)

class Users(db):
    __tablename__ = 'users'
    id = Column(Integer(), primary_key=True)
    name = Column(VARCHAR(32))
    password = Column(VARCHAR(32))
    created_at = Column(DateTime())
    def __init__(self, name, password):
        self.name = name
        self.password = hashed(name,password,100)
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
    deleted_at = Column(DateTime(), default=null)

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
    session.add(user)
    session.commit()

def check_user(name,password):
    print(name,password)
    user = session.query(Users).filter(Users.name==name).filter(Users.password==hashed(name,password,100)).first()
    return user

def add_room(room):
    session.add(room)
    session.commit()

def del_room(ids):
    for id in ids:
        room = session.query(Rooms).filter(Rooms.user_id==ss['id']).filter(Rooms.id==id).first()
        room.deleted_at = datetime.datetime.now()
    session.commit()

Session = sessionmaker(bind=engine)
db_session = Session()
db.metadata.create_all(engine)