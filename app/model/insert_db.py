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



class Book:
    id: str
    title: str
    author: str
    publisher: str
    original_title: str
    translator: str
    pub_year: str
    pages: int
    price: int
    binding: str
    isbn: str
    author_intro: str
    book_intro: str
    content: str
    tags: [str]
    pictures: [bytes]

    def __init__(self):
        self.tags = []
        self.pictures = []


class BookDB:
    def __init__(self, large: bool = False):
        parent_path = os.path.dirname(os.path.dirname(__file__))
        self.db_s = os.path.join(parent_path, "../fe/data/book.db")
        self.db_l = os.path.join(parent_path, "../fe/data/book_lx.db")
        if large:
            self.book_db = self.db_l
        else:
            self.book_db = self.db_s

    def get_book_count(self):
        conn = sqlite.connect(self.book_db)
        cursor = conn.execute(
            "SELECT count(id) FROM book")
        row = cursor.fetchone()
        return row[0]

    def get_book_info(self, start, size) -> [Book]:
        books = []
        conn = sqlite.connect(self.book_db)
        cursor = conn.execute(
            "SELECT id, title, author, "
            "publisher, original_title, "
            "translator, pub_year, pages, "
            "price, currency_unit, binding, "
            "isbn, author_intro, book_intro, "
            "content, tags, picture FROM book ORDER BY id "
            "LIMIT ? OFFSET ?", (size, start))
        for row in cursor:
            book = Book()
            book.id = row[0]
            book.title = row[1]
            book.author = row[2]
            book.publisher = row[3]
            book.original_title = row[4]
            book.translator = row[5]
            book.pub_year = row[6]
            book.pages = row[7]
            book.price = row[8]

            book.currency_unit = row[9]
            book.binding = row[10]
            book.isbn = row[11]
            book.author_intro = row[12]
            book.book_intro = row[13]
            book.content = row[14]
            tags = row[15]

            picture = row[16]

            for tag in tags.split("\n"):
                if tag.strip() != "":
                    book.tags.append(tag)
            for i in range(0, random.randint(0, 9)):
                if picture is not None:
                    encode_str = base64.b64encode(picture).decode('utf-8')
                    book.pictures.append(encode_str)
            books.append(book)
            # print(tags.decode('utf-8'))

            # print(book.tags, len(book.picture))
            # print(book)
            # print(tags)

        return books


if __name__ == '__main__':
    b = BookDB(False)
    books = b.get_book_info(0, b.get_book_count())

    engine = create_engine(DbURL)
    session = create_session(engine)

    # 新建商店：之后运行可以不需要
    User = Users(UserId="test", UserName="test", HaveStore=True, Balance=10, Password="test", Terminal="test")
    session.add(User)
    session.commit()
    Store = Stores(StoreId="fortest", UserId="test", Balance=0)
    session.add(Store)
    session.commit()

for i in range(0, b.get_book_count()):
    book = books[i]

    # StoreBoos中储存图片的id，用"|"分割，图片储存在BookPicture中
    # 因为有外键约束，所以在插入数据信息之后再插入图片
    PicIdStr = ""
    for p in range(0, len(book.pictures)):
        picstr = book.id+"pic"+str(p)
        # BookPicture = BookPictures(PictureId=picstr, BookId=book.id, Address=book.pictures[p])
        # session.add(BookPicture)
        PicIdStr = PicIdStr + picstr
    # session.commit()

    # 所有tag合并为一个字符串
    tagStr = ""
    for t in range(0, len(book.tags)):
        tagStr = tagStr + book.tags[t]+"|"

    # 把一条数据信息插入数据库
    StoreBook = StoreBooks(StoreId="fortest", Stock=1, BookId=book.id, Title=book.title, Author=book.author, Publisher=book.publisher,
                           OriginalTitle=book.original_title, Translator=book.translator, PubYear=book.pub_year, Pages=book.pages,
                           Price=book.price, Binding=book.binding, Isbn=book.isbn, AuthorIntro=book.author_intro, BookIntro=book.book_intro,
                           Content=book.content, Tags=tagStr, PictureId=PicIdStr)
    session.add(StoreBook)
    session.commit()

    # 插入图片
    for p in range(0, len(book.pictures)):
        picstr = book.id+"pic"+str(p)
        BookPicture = BookPictures(PictureId=picstr, BookId=book.id, Address=book.pictures[p])
        session.add(BookPicture)
        session.commit()





'''
原始建立索引的指令
-- ALTER TABLE "StoreBooks" add column ts_search tsvector;
-- UPDATE "StoreBooks" SET ts_search =
-- to_tsvector('zhparser', coalesce("Tags",'') || ' ' || coalesce("Title",'') || coalesce("Content",'') || coalesce("BookIntro",''));
-- CREATE INDEX idx_ts_seach ON "StoreBooks" USING gin(ts_search);
SELECT * FROM "StoreBooks" WHERE ts_search @@ to_tsquery('金庸');'''