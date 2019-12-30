import os
import sqlite3 as sqlite
import random
import base64
import simplejson as json
import logging

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Float, DateTime, create_engine, \
    PrimaryKeyConstraint, desc, \
    Sequence
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import DatabaseError
from app.model.Global import DbURL
from app.model.create_db import create_session, StoreBooks, Stores, BookPictures, Users

if __name__ == '__main__':
    engine = create_engine(DbURL)
    session = create_session(engine)
    keyword = '金庸'
    store_id = 'fortest'
    sql_str = "SELECT \"BookId\",\"Title\" FROM \"StoreBooks\" WHERE ts_search @@ to_tsquery('%s') AND \"StoreId\"='%s'" % (
    keyword, store_id)

    result = session.execute(sql_str)

    print(result.fetchall()[0])

    session.commit()

