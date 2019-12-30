import pytest

from fe.access.buyer import Buyer
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.book import Book
import uuid
from fe.access.order import Order
from fe.access.auth import Auth
from fe import conf
class TestMyOrder:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.buyer_id = "test_payment_buyer_id_{}".format(str(uuid.uuid1()))
        self.terminal = "terminal_" + self.buyer_id
        self.buyer_password = "password_"+self.buyer_id
        self.seller = None
        self.buyer = register_new_buyer(self.buyer_id, self.buyer_password)
        self.token = self.buyer.token
        self.order = Order(conf.URL)
        self.order_num = 10

        for i in range(self.order_num):
            self.store_id = "test_payment_store_id_{}".format(str(uuid.uuid1()))
            self.seller_id = "test_payment_seller_id_{}".format(str(uuid.uuid1()))
            gen_book = GenBook(self.seller_id, self.store_id)
            self.seller = gen_book.seller
            ok, buy_book_id_list = gen_book.gen(non_exist_book_id=False, low_stock_level=False, max_book_count=5)
            self.buy_book_info_list = gen_book.buy_book_info_list
            assert ok
            code, self.order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
            assert code == 200
        yield

    def test_ok(self): # 
        # code = self.order.user_cancel_order(self.buyer_id, self.token)
        code = self.buyer.add_funds(300)
        assert code == 200
        code, token = Auth(conf.URL).login(self.buyer_id, self.buyer_password, self.terminal)
        assert code == 200
        code = self.order.my_orders(self.buyer_id, token)
        assert code == 200

    def test_authorization_error(self):  # 授权失败，token
        buyer_id = self.buyer_id+"dfdf"
        code = self.order.my_orders(buyer_id, self.token)
        assert code != 200

    

    
