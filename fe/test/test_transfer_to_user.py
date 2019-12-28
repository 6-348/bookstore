import pytest

from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer

import uuid

class TestTransfer:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        # self.seller_id = "test_new_order_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_new_order_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_new_order_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        self.buyer = register_new_buyer(self.buyer_id, self.password)
        self.gen_book = GenBook(self.seller_id, self.store_id)
        yield