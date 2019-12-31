# buyer 相关的功能
"""
* buyer
* 充值、下单、付款、提现、确认收货、转账到用户

"""
import app.model.Global as Global
import numpy as np
import json 
from app.model.create_db import Users,Orders,Stores,OrderBooks,StoreBooks,create_session
from app.model.user import UsersMethod
import app.model.error as error
import logging
from datetime import datetime
from sqlalchemy import and_,update,create_engine
from sqlalchemy.orm import sessionmaker

class Buyer:
    def __init__(self):
        self.engine = create_engine(Global.DbURL,pool_size=20, max_overflow=0)
        self.user_method = UsersMethod()
    
    # 下单 
    def neworder(self,user_id,store_id,books,token):
        '''
        @params: user_id,store_id,books = [{"id": id_count_pair[0], "count": id_count_pair[1]},]
        @exceptions: token错误，store_id 不存在，书不存在，库存不足，重复下单,user_id 不存在
        操作：（45是一个事务）
        4. 减少库存
        5. Order, OrderBooks表格中新建项(新建order的时间是"当前时间+timeout时间期限"
        '''
        # logging.debug("user_id:{},store_id:{}".format(user_id, store_id))
        timestr = datetime.now().strftime('%a-%b-%d-%H-%M-%S.%f')
        order_id =store_id+user_id+timestr+str(np.random.randint(0, 100)) # order_id 的生成
        # order_id = store_id + user_id + timestr  # order_id 的生成
        code,message = self.user_method.check_token(token, user_id)
        if code!=200:
            # logging.debug("{}:{}".format(code, message))
            return code, message, order_id
        try:
            session = create_session(self.engine)
            line = session.query(Stores).filter(Stores.StoreId==store_id).first()
            if line==None:
                code, meassge = error.error_invalid_store_id(store_id)
                # logging.debug("{}:{}".format(code, message))
                return code, message, order_id
            userline = session.query(Users).filter(Users.UserId==user_id).first()
            if userline ==None:
                code, meassge = error.error_non_exist_user_id(user_id)
                # logging.debug("{}:{}".format(code, message))
                return code, message, order_id
            Amount = 0
            for book in books:
                book_id = book["id"]
                count = book["count"]
                bookline = session.query(StoreBooks).filter(and_(StoreBooks.BookId==book_id,StoreBooks.StoreId == store_id)).first()
                if bookline==None:
                    code, meassge = error.error_non_exist_book_id(book_id)
                    # logging.debug("{}:{}", code, message)
                    return code, message, order_id
                elif bookline.Stock < count:
                    code, meassge =error.error_non_exist_book_id(book_id)
                    # logging.debug("{}:{}", code, message)
                    return code, message, order_id
                else:
                    Amount+=bookline.Price * count 
            #修改数据库 Orders 增加一条， OrderBooks，每个BookId 增加一条
            order = Orders(OrderId= order_id, StoreId =store_id,UserId = user_id,Status = "1", Amount= Amount,Deadline = datetime.now()+Global.order_timeout_delta)
            session.add(order)
            session.commit()
            for book in books:
                book_id = book["id"]
                count = book["count"]
                orderbook = OrderBooks(OrderId=order_id, BookId = book_id, Count=count)
                session.add(orderbook)
            session.commit()
        except Exception as e:
            # logging.error("app.model.buy.py line 64 {}".format(e))
            session.rollback()
            return error.error_and_message(100, "commit fail"), order_id
        finally:
            session.close()
        code,meassge = error.success("neworder")
        # logging.debug(message)
        return code, message, order_id


    # 付款
    def payment(self,user_id,order_id,password,token):
        '''
        @exceptions: 余额不足,token 对不上，order_id 无效，密码不对
        事务：
        4. 减少买家余额
        5. 修改order.status
        '''
        code,message = self.user_method.check_token(token, user_id)
        if code!=200:
            # print(98)
            return code,message
        try:
            session = create_session(self.engine)
            orderlines = session.query(Orders).filter(Orders.OrderId==order_id)
            orderline = orderlines[0]
            userlines = session.query(Users).filter(Users.UserId==user_id)
            userline = userlines[0]
            if orderline == None :
                # print(104)
                return error.error_invalid_order_id(order_id)
            elif orderline.OrderId != order_id or orderline.Status !="1":
                # print(107)
                return error.error_invalid_order_id(order_id)
            elif userline.Password != password:
                # print(110)
                return error.error_authorization_fail()
            elif userline.Balance < orderline.Amount:
                # print(113)
                return error.error_not_sufficient_funds(order_id)
            else:   # 修改数据库
                orderline.Status = "2"
                userline.Balance-=orderline.Amount
                orderlines.update({"Status": "2"})
                userlines.update({"Balance": userline.Balance})
                session.commit()
        except Exception as e:
            # logging.error("app.model.Payment.py line 101 {}".format(e))
            session.rollback()
            return error.error_and_message("110","commit fail")
        finally:
            session.close()
        logging.debug("payment successfully")
        return error.success("Payment")


    # 充值
    def add_funds(self,user_id,password,add_value,token):
        '''
        @params: user_id , password, add_value
        exception: token,password,add_value>0?, 
        3. 修改用户金额
        '''
        # logging.debug("topup has run")
        code,message = self.user_method.check_token(token, user_id)
        if code!=200:
            print(135)
            return code,message
        try:
            session = create_session(self.engine)
            line = session.query(Users).filter(Users.UserId==user_id)
            userline = line[0]
            if userline.Password!=password:
                print(140)
                return error.error_authorization_fail()
        # 修改数据库
            line.update({"Balance": userline.Balance+add_value})
            session.commit()
        except Exception as e:
            # logging.error("app.model.Addfund.py line 130{}".format(e))
            session.rollback()
            print(152)
            return error.error_and_message(110, "commit fail")
        finally:
            session.close()
        print(156)
        return error.success("Addfund")


    # 下为扩展接口
    # 提现
    def withdraw(self,user_id, money, password, token):
        '''
        @exception: token?, password? 余额不足？
        @params: user_id, money, password, token
        减少用户balance
        '''
        logging.debug("withdraw has run")
        code,message = self.user_method.check_token(token, user_id)
        if code!=200:
            return code,message
        try:
            session = create_session(self.engine)
            line = session.query(Users).filter(Users.UserId==user_id).first()
            if line.Password !=password:
                return error.error_authorization_fail()
            elif money<=0:
                return error.error_invalid_value(money)
            elif line.Balance<money:
                return error.error_not_sufficient_funds("about withdraw"+user_id)
        # 修改数据库
            line.update({"Balance":line.Balance-money})
            session.commit()
        except Exception as e:
            logging.error("app.model.withdraw.py line 161 {}".format(e))
            session.rollback()
        finally:
            session.close()       
        return error.success("withdraw")
        
    # 确认收货
    def confirm_reception(self,user_id,order_id,password,token):
        '''
        @exception: token? order_id 存在？ Orders.Status==3? password right?
        @params: order_id, user_id, password,token
        3. 增加商户金额
        4. 修改orders.status为已确认收货
        '''
        logging.debug("withdraw has run")
        code,message = self.user_method.check_token(token, user_id)
        if code!=200:
            print(210)
            return code, message
        try:
            session = create_session(self.engine)
            orderlines = session.query(Orders).filter(Orders.OrderId==order_id)
            userlines = session.query(Users).filter(Users.UserId==user_id)
            userline = userlines[0]
            orderline = orderlines[0]
            if orderlines == None:
                # print(218)
                return error.error_invalid_order_id(order_id)
            if orderline.Status!="3":
                # print(222)
                return error.error_order_steate_not_right(orderline.Status)
            if orderline.UserId != user_id:
                # print(220)
                return error.error_invalid_order_id(order_id)
            if userlines == None:
                # print(224)
                return error.error_exist_user_id(user_id)
            if userline.Password!=password:
                # print(228)
                return error.error_authorization_fail()
            store_id = orderline.StoreId
            storelines = session.query(Stores).filter(Stores.StoreId == store_id)
            storeline = storelines[0]
             # 修改数据库
            storelines.update({"Balance": storeline.Balance+orderline.Amount})
            orderlines.update({"Status": "4"})
            session.commit()
            # logging.debug("confirm reception successfully ")
            return error.success("confirm_reception")
        except Exception as e:
            # logging.error("app.model.confirm_reception.py line 197 {}".format(e))
            session.rollback()
            return error.error_and_message(110, "commit fail")
        finally:
            session.close()       


