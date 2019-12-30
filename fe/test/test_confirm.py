import pytest

from fe.access.buyer import Buyer
from fe.access.seller import Seller
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.new_seller import register_new_seller
from fe.access.book import Book
import uuid
from fe.access.auth import Auth
from fe import conf

class TestConfirm:
    seller_id: str
    buyer_id: str
    store_id: str
    buyer_id: str
    seller_password: str
    buyer_password: str
    buy_book_info_list: [Book]
    total_price: int
    order_id: str
    buyer: Buyer
    seller: Seller

    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_confirm_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_confirm_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_confirm_buyer_id_{}".format(str(uuid.uuid1()))
        self.terminal = str(uuid.uuid1())
        self.buyer_password = self.buyer_id
        self.buyer = register_new_buyer(self.buyer_id, self.buyer_password)
        # gen_book是个类实例 绑定seller_id和store_id
        gen_book = GenBook(self.seller_id, self.store_id)
        self.seller = gen_book.seller
        self.seller_password = self.seller.password
        # 调用类方法gen生成要买的书列表
        ok, buy_book_id_list = gen_book.gen(non_exist_book_id=False, low_stock_level=False, max_book_count=5)
        self.buy_book_info_list = gen_book.buy_book_info_list
        assert ok
<<<<<<< HEAD
        # 下单
        code, self.order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
=======
        b = register_new_buyer(self.buyer_id, self.buyer_password)
        s = register_new_seller(self.seller_id, self.seller_password)
        self.buyer = b
        self.seller = s
        code, self.token = self.auth.login(self.buyer_id, self.buyer_password, self.terminal)
        assert code == 200
        code, self.order_id = b.new_order(self.store_id, buy_book_id_list)
>>>>>>> 3cbda147243aad6cc52745e6f48a541f8facbf90
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

