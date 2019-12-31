import pytest

from fe.access.buyer import Buyer
from fe.access.new_buyer import register_new_buyer
import uuid
from fe.access.auth import Auth
from fe import conf

class TestConfirm:
    user_id: str
    user_password: str
    user: Buyer

    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.user_id = "test_confirm_buyer_id_{}".format(str(uuid.uuid1()))
        self.terminal = str(uuid.uuid1())
        self.password = self.user_id
        self.user = register_new_buyer(self.user_id, self.password)
        self.token = self.user.token
        self.fund = 20
        code = self.user.add_funds(20)
        assert code == 200
        yield


'''@exception: token?password?'''
    def test_authorization_error(self):
        password = self.password+"@@"
        code = self.buyer.withdraw(self.user_id,self.fund,self.password,self.token)
        assert code == 401

'''@exception: 余额不足?'''
    def test_not_suff_fund_error(self):
        fund = self.fund+20
        code = self.buyer.withdraw(self.user_id,fund,self.password,self.token)
        assert code == 519

'''@exception: 金额为负?'''
    def test_invalid_amount_error(self):
         code = self.buyer.withdraw(self.user_id,-10,self.password,self.token)
        assert code == 525


