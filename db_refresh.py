from sqlalchemy import *
from sqlalchemy import Column, Integer, VARCHAR, DateTime, TEXT
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
import datetime, hashlib, psycopg2
from pysrc.search2 import getter
from pysrc.test import del_all_list
from flask import session as ss
import pandas as pd

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
del_all_list()

sl = getter()
sl.to_sql('search_list', con=engine, if_exists='append')
del sl