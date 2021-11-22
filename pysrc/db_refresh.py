from sqlalchemy import *
from sqlalchemy import Column, Integer, VARCHAR, DateTime, TEXT
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
import datetime, hashlib, psycopg2
from pysrc.search2 import getter
from flask import session as ss
import pandas as pd

def exe():
    database = 'dgp2oe0v7u7ba'
    user = 'fcjytqjkmrdcth'
    password = 'd0d4acde298c07fedd9acf037ec024ffd15a8ee6ea2ea07876d8ab7dc840b256'
    host = 'ec2-23-23-181-251.compute-1.amazonaws.com'
    port = '5432'

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

    class search_list2(db):
        __tablename__ = "search_list2"
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

    session.query(search_list2).delete()
    session.commit()

    sl = getter()
    sl.to_sql('search_list2', con=engine, if_exists='append', index=False)