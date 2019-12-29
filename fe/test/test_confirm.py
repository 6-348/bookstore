import pytest

from fe.access.buyer import Buyer
from fe.access.seller import Seller
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.new_seller import register_new_seller
from fe.access.book import Book
import uuid


class TestConfirm:
    # def __init__(self):
    #     self.engine = create_engine(Global.DbURL)
    #     # self.user_method = UsersMethod()

    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_confirm_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_confirm_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_confirm_buyer_id_{}".format(str(uuid.uuid1()))
        self.seller_password = self.seller_id
        self.buyer_password = self.buyer_id
        # gen_book是个类实例 绑定seller_id和store_id
        gen_book = GenBook(self.seller_id, self.store_id)
        # 调用类方法gen生成要买的书列表
        ok, buy_book_id_list = gen_book.gen(non_exist_book_id=False, low_stock_level=False, max_book_count=5)
        self.buy_book_info_list = gen_book.buy_book_info_list
        assert ok
        s = register_new_seller(self.seller_id, self.seller_password)
        b = register_new_buyer(self.buyer_id, self.buyer_password)
        self.buyer = b
        self.seller = s
        code, self.order_id = b.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        # 金额要用到的地方：充值后才能付款
        self.total_price = 0
        for item in self.buy_book_info_list:
            book: Book = item[0]
            num = item[1]
            self.total_price = self.total_price + book.price * num
        code = self.buyer.add_funds(self.total_price)
        assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        yield

    def test_ok(self):
        # code = self.buyer.add_funds(self.total_price)
        # assert code == 200
        # code = self.buyer.payment(self.order_id)
        # assert code == 200
        code = self.seller.delivery_books(self.seller_id, self.order_id)
        assert code == 200
        code = self.buyer.confirm_reception(
            self.buyer_id, self.order_id, self.buyer_password)
        assert code == 200

    '''@exception: password right?'''
    def test_authorization_error(self):
        # code = self.buyer.add_funds(self.total_price)
        # assert code == 200
        # code = self.buyer.payment(self.order_id)
        # assert code == 200
        code = self.seller.delivery_books(self.seller_id,self.order_id)
        assert code == 200
        self.buyer_password = self.buyer_password + "_x"
        code = self.buyer.confirm_reception(self.buyer_id,self.order_id,self.buyer_password)
        assert code != 200

    '''@exception: order_id exist?'''
    def test_order_id_error(self):
        # code = self.buyer.add_funds(self.total_price)
        # assert code == 200
        # code = self.buyer.payment(self.order_id)
        # assert code == 200
        code = self.seller.delivery_books(self.seller_id,self.order_id)
        assert code == 200
        self.order_id = self.order_id + "_Ooo"
        code = self.buyer.confirm_reception(self.buyer_id,self.order_id,self.buyer.password)
        assert code != 200


    '''@exception: no delivery?'''
    def test_order_status_error(self):
        code = self.buyer.confirm_reception(self.buyer_id,self.order_id,self.buyer.password)
        assert code != 200

    '''@exception: repeat confirm'''
    def test_reppeat_confirm(self):
        code = self.seller.delivery_books(self.seller_id,self.order_id)
        assert code == 200
        code = self.buyer.confirm_reception(self.buyer_id,self.order_id,self.buyer.password)
        assert code == 200
        code = self.buyer.confirm_reception(self.buyer_id,self.order_id,self.buyer.password)
        assert code != 200

