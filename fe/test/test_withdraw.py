import pytest

from fe.access.buyer import Buyer
from fe.access.new_buyer import register_new_buyer
import uuid
from fe.access.auth import Auth
from fe import conf

class TestWithdraw:
    user_id: str
    user_password: str
    user: Buyer

    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.user_id = "test_withdraw_buyer_id_{}".format(str(uuid.uuid1()))
        self.terminal = str(uuid.uuid1())
        self.password = self.user_id
        self.user = register_new_buyer(self.user_id, self.password)
        self.token = self.user.token
        self.fund = 20
        code = self.user.add_funds(20)
        assert code == 200
        yield

    def test_ok(self):
        code = self.user.withdraw(self.user_id,self.fund,self.password)
        assert code == 200

    '''@exception: token?password?'''
    def test_authorization_error(self):
        password = self.password+"@@"
        code = self.user.withdraw(self.user_id,self.fund,password)
        assert code == 401

    '''@exception: 余额不足?'''
    def test_not_suff_fund_error(self):
        fund = self.fund+20
        code = self.user.withdraw(self.user_id,fund,self.password)
        assert code == 519

    '''@exception: 金额为负?'''
    def test_invalid_amount_error(self):
         code = self.user.withdraw(self.user_id,-10,self.password)
         assert code == 525


