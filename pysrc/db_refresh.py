from sqlalchemy import *
from sqlalchemy import Column, Integer, VARCHAR, DateTime, TEXT
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
import datetime, hashlib, psycopg2
from pysrc.search2 import getter
from flask import session as ss
import pandas as pd
from pysrc import env

def exe():
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

    sl = getter()
    sl.to_sql('search_list', con=engine, if_exists='append')