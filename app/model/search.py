import logging
from sqlalchemy import create_engine
from sqlalchemy.exc import DatabaseError

from app.model.create_db import StoreBooks, BookPictures, create_session
from app.model.Global import DbURL, SECRET_KEY
import app.model.error as error

class SearchMethod():
    def __init__(self):
        self.engine = create_engine()

    def search_store(self, store_id:str, keyword:str) :
        try:
            book_list = []
            session = create_session(self.engine)
            sql_str = "SELECT \"BookId\",\"Title\" FROM \"StoreBooks\" WHERE ts_search @@ to_tsquery('%s') AND \"StoreId\"='%s'" % (keyword, store_id)
            result = session.execute(sql_str)
            book_list = result.fetchall()
            session.commit()
            return "ok", book_list
        except DatabaseError as e:
            logging.debug(e)
            return "not ok", book_list
        finally:
            session.close()

    def search_all(self, keyword: str):
        try:
            session = create_session(self.engine)
            sql_str = "SELECT \"BookId\",\"Title\" FROM \"StoreBooks\" WHERE ts_search @@ to_tsquery('%s')" % (keyword)
            result = session.execute(sql_str)
            book_list = result.fetchall()
            session.commit()
            return "ok", book_list
        except DatabaseError as e:
            logging.debug(e)
            return "not ok", book_list
        finally:
            session.close()

