from fe import conf
from fe.access import order, auth


def register_new_order(user_id, password) -> order.Order:
    a = auth.Auth(conf.URL)
    # code = a.register()
    assert code == 200
    s = buyer.Buyer(conf.URL, password)
    return s
