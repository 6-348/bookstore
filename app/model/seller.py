import app.model.Global as Global
import json 
from app.model.create_db import Users,BookPictures,Orders,Stores,OrderBooks,StoreBooks,create_session
from app.model.user import UsersMethod
import app.model.error as error
import logging
from datetime import datetime
from sqlalchemy import and_,update,create_engine
from sqlalchemy.orm import sessionmaker
import numpy as np
import base64
def to_dict(result:object,dropwords:list)->dict:
    dic = {}
    for att in dir(result):
        if att.startswith("_") or att in dropwords:
            continue
        value = getattr(result,att)
        dic[att] = value
    return dic
def save_img(picture:bytes,picture_address):
    # 图片保存参考：https://blog.csdn.net/mingyuli/article/details/82853812
    # 待完成函数，存储图片
    img = base64.b64decode(picture)
    file = open(picture_address, 'wb')
    file.write(img)
    file.close()

# a = StoreBooks()
# print(to_dict(a,[]))
class Seller():
    def __init__(self):
        self.engine = create_engine(Global.DbURL)
        self.user_method = UsersMethod()

    # 创建商铺
    def create_store(self, user_id,store_id,token):
        '''
        @ exception : token?  store_id exist? 
        @request: user_id,store_id,token
        3. stores创建新的一行
        '''
        code,message = self.user_method.check_token(token, user_id)
        if code!=200:
            logging.debug("stop in check_token")
            return code,message
        try:
            session = create_session(self.engine)
            storeline = Stores(StoreId=store_id,UserId=user_id,Balance=0)
            session.add(storeline)
            session.commit()
        except Exception as e:
            logging.error("app.model.seller.py create_store line 31: {}".format(e))
            session.rollback()
            return error.error_exist_store_id(store_id)
        finally:
            session.close()
        logging.debug("create store successfully")
        return error.success("create_stores")

    # 添加书籍信息
    def add_bookinfo(self,user_id, store_id, book_info:dict, stock_level,token):
        '''
        @exception token?store_id exist? user_id 和 store_id是否匹配？
         每本书的Stock >=0?  bookinfo 是否缺少必填项？book_id exist?

    !!谁写的话，用数据库自己测试一下，34额错误数据库返回信息是否相同，如果不同可以直接插入
        3. 检查不能为空的bookinfo是否为空
        4. 检查book_id是否存在

        5. 合并tag为字符串， 以#为分隔符
        6. 插入到StoreBooks # 图片保存参考：https://blog.csdn.net/mingyuli/article/details/82853812
        7. 插入到Pictures db
        @request: user_id, store_id, book_info(dict), stock_level
        :return:
        '''
        logging.debug("add_book has run")
        code,message = self.user_method.check_token(token, user_id)
        if code!=200:
            logging.debug("stop in check_token")
            return code,message
        try:
            session = create_session(self.engine)
            storeline = session.query(Stores).filter(Stores.StoreId==store_id).first()
            logging.debug("store_id"+store_id)
            if storeline ==None:
                return error.error_non_exist_store_id(store_id)
            if storeline.UserId !=user_id:
                return error.error_exist_user_id(user_id)# uer_id 和store_id不匹配
            # 插入bookline 如果两种情况不成功，1. 部分信息的nullable 不满足；2. BookId 已经存在
            #-----注意插入的时候要考虑，book_info 里面的属性不完全的情况
            book_id = book_info['id']
            logging.debug("book_id: {}".format(book_id))
            bookline = session.query(StoreBooks).filter(and_(StoreBooks.BookId==book_info["id"],StoreBooks.StoreId==store_id)).first()
            if bookline !=None:
                logging.debug(bookline)
                return error.error_exist_book_id(book_info["id"])
            # 修改数据库：            
                # tags
            Tags = None
            if "tags" not in list(book_info.keys()):
                Tags = None
            else:
                Tags = ""
                for tag in book_info['tags']:
                    Tags+=tag+","
                # pictures:BookPictures
            picture_id_list = []
            picobj_list = []
            if "pictures" not in list(book_info.keys()):
                logging.debug("i don't have pictures")
                picture_id_list = []
            else:
                # logging.debug("i have pictures: {}".format(book_info["pictures"]))
                difcode = 0
                for picture in book_info["pictures"]:
                    difcode+=1
                    timestr = datetime.now().strftime('%a-%b-%d-%H-%M-%S.%f')
                    picturename = store_id+book_id+timestr+str(difcode)+ str(np.random.randint(0,100))+".png"

                    picture_address = Global.PicturePath+picturename
                    # save_img(picture,picture_address)
                    logging.debug("picture_address:{}"+picture_address)
                    picture_id = picturename
                    logging.debug("pcitre_id----------->{}".format(picture_id))
                    picobj = BookPictures(PictureId= picture_id,Address= picture_address,BookId = book_id)
                    picobj_list.append(picobj)
                    picture_id_list.append(picture_id)            
                 # 防止book_info 里面内容不完整，所以补全 
                 # StoreBooks 
            map_testtodb = {
                "id":"BookId",
                "title":"Title",
                "author" :"Author",
                "publisher":"Publisher",
                "original_title":"OriginalTitle",
                "translator": "Translator",
                "pub_year":"PubYear",
                "pages": "Pages",
                "price": "Price",
               "binding": "Binding",
                "isbn": "Isbn",
                "author_intro": "AuthorIntro",
                "book_intro":  "BookIntro",
                "content": "Content",
                "tags": "Tags",
            }
            book = StoreBooks(StoreId = store_id,
            BookId = book_id,Stock = stock_level, Tags = Tags)

            keylist = list(book_info.keys())
            keylist.remove("tags")
            keylist.remove("pictures")
            for info in keylist:
                if info not in list(map_testtodb.keys()):
                    continue
                db_attr = map_testtodb[info]
                # logging.debug(db_attr+":"+info+": {}".format(book_info[info]))
                setattr(book, db_attr, book_info[info])
            if picture_id_list==[]:
                session.add(book)
            else:
                for picobj in picobj_list:
                    setattr(book, "PictureId", picobj.PictureId)
                    logging.debug("book_id"+book.BookId + "picobj"+picobj.BookId)
                    session.add(book)
                    session.add(picobj)
            session.commit()
        except Exception as e:
            logging.error(e)
            logging.error("app.model.seller.py add_book line 134: {}".format(e))
            session.rollback()
            # logging.error("invalid book info{}".format(book_info))
            return error.error_and_message(530,"invalid book info")
        finally:
            session.close()
        logging.debug("add book successfully")
        return error.success("add_book")
     # 添加库存
    def add_stock(self,user_id,store_id,book_id,add_stock_level,token):
        '''
        @exception token? add_stock_level >0? book_id exist? user_id 和 store_id匹配？
        0. check_token
        1. 检查add_stock_level是否大于0
        2. Stores: 检查store_id是否存在，对应的user_id是否匹配
        3. 根据book_id查询书籍对象，看是否存在，存在就更新库存
        @request: user_id, store_id, book_id, add_stock_level
        :return:
        '''
        logging.debug("i am add_stock")
        # check token
        code,message = self.user_method.check_token(token, user_id)
        if(code!=200):
            logging.debug("stop in check_token")
            return code,message
        # add_stock_level >0?
        if add_stock_level<=0:
            return error.error_invalid_value(add_stock_level)
        try: 
            session = create_session(self.engine)
            bookline = session.query(StoreBooks).filter(and_(StoreBooks.BookId==book_id,StoreBooks.StoreId==store_id)).first()
            if bookline==None: # book_id exist?
                logging.debug("book_id not exist")
                return error.error_non_exist_book_id(book_id)
            storeline = session.query(Stores).filter(Stores.StoreId==store_id).first()
            if storeline.UserId!=user_id: # book_id 和 user_id 不匹配
                logging.debug("book_id 和 user_id 不匹配")
                return error.error_invalid_store_id(store_id)
            # 修改数据库：
            bookline.update({"Stock": bookline.Stock+add_stock_level})
            session.commit()
        except Exception as e:
            logging.error("app.model.seller.py add_stock line174 {}".format(e))
            session.rollback()
        finally:
            session.close()
        logging.debug("add stock successfully")
        return error.success("add Stock")

# 扩展接口
    def delivery_books(self,seller_id:str, order_id:str, token: str)->(str,str):
        # check token
        code,message = self.user_method.check_token(token,seller_id)
        if(code!=200):
            logging.debug("stop in check_token")
            return code,message
        try: 
            session = create_session(self.engine)
            # 该订单不存在
            orderline  = session.query(Orders).filter(Orders.OrderId == order_id)
            order = orderline[0]
            if order == None:
                return error.error_invalid_order_id(order_id)
            # 订单非已付款的状态
            if order.Status=='3':
                return error.error_repeated_operation("delivery books")
            if order.Status=='1':
                return error.error_order_steate_not_right("Unpayed order")
            if order.Status=='5':
                return error.error_order_steate_not_right("Fail order")
            if order.Status=='4':
                return error.error_order_steate_not_right("finished order")
            # 修改订单状态：
            orderline.update(
                {Orders.Status: "3"}
            )
            session.commit()
            print(error.success("Dlivery books"))
            return error.success("Dlivery books")
        except Exception as e:
            logging.error("app.model.seller.py dlivery_books line 185:{}".format(e))
            session.rollback()
            return error.error_and_message("110","commit fail")
        finally:
            session.close()
