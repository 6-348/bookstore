import pytest

from fe.access.buyer import Buyer
from fe.access.seller import Seller
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.book import Book
import uuid



class TestTransfer:
    seller_id: str
    store_id: str
    buyer_id: str
    password: str
    buy_book_info_list: [Book]
    total_price: int
    order_id: str
    buyer: Buyer
    seller: Seller

    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_transfer_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_transfer_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_transfer_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.buyer_id
        gen_book = GenBook(self.seller_id, self.store_id)
        ok, buy_book_id_list = gen_book.gen(non_exist_book_id=False, low_stock_level=False, max_book_count=5)
        self.buy_book_info_list = gen_book.buy_book_info_list
        assert ok
        self.buyer= register_new_buyer(self.buyer_id, self.password)
        self.seller = gen_book.seller
        self.store_id = gen_book.store_id
        code,self.order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200

        self.total_price = 0
        for item in self.buy_book_info_list:
            book: Book = item[0]
            num = item[1]
            self.total_price = self.total_price + book.price * num

        code = self.buyer.add_funds(self.total_price)
        assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.seller.delivery_books(self.seller_id,self.order_id)
        assert code == 200
        code = self.buyer.confirm_reception(self.buyer_id,self.order_id,self.password)
        assert code == 200
        yield


        def test_ok(self):
            code = self.seller.transfer_to_user(self.seller_id,self.store_id,self.seller.password,self.total_price)
            assert code == 200

        '''@exception： 401 password right? '''
        def test_authorization_error(self):
            password = self.seller.password+'_x'
            code = self.seller.transfer_to_user(self.seller_id,self.store_id,password,self.total_price)
            assert code == 401

        '''@exception： 511 store_id exist?'''
        def test_storeid_error(self):
            store_id = self.store_id +"_ss"
            code = self.seller.transfer_to_user(self.seller_id,store_id,self.seller.password,self.total_price)
            assert code == 511

        '''@exception： 519 balance suffient?'''
        def test_balance_exceed_error(self):
            amount = self.total_price + 20
            code = self.seller.transfer_to_user(self.seller_id,self.store_id,self.seller.password,amount)
            assert code == 519

        '''@exception:  525 amount<0?'''
        def test_invalid_amount_error(self):
            amount = -20
            code = self.seller.transfer_to_user(self.seller_id,self.store_id,self.seller.password,amount)
            assert code == 525
