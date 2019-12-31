"""
说明：
* 作用：创建 flaskr 文件夹并且文件夹内添加 __init__.py 文件。
__init__.py 有两个作用：一是包含应用工厂；二是 告诉 Python flaskr 文件夹应当视作为一个包。

* 可参考助教代码： /be/server.py
* 下面是官方文档的代码，数据库的地址需要修改，app 的config里面还要写啥
"""

import os
from logging.handlers import TimedRotatingFileHandler
from flask import Flask
from flask import Blueprint
from flask import request

import logging
from logging import Logger
from logging import FileHandler

import app.view.auth as auth
import app.view.buyer as buyer
import app.view.seller as seller
import app.view.order as order
from  app.model.Global import DbURL
from sqlalchemy import create_engine

bp_shutdown = Blueprint("shutdown", __name__)


def shutdown_server():
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()


@bp_shutdown.route("/shutdown")
def be_shutdown():
    shutdown_server()
    return "Server shutting down..."

def create_app(test_config=None):
    # 设置log
    logging.basicConfig(filename='flask.log', level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler = logging.StreamHandler()
    logging.getLogger().addHandler(handler)


    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config['SQLALCHEMY_DATABASE_URI'] = DbURL
    app.config['SECRET_KEY'] = 'deddddddddddv'
    app.config['DEBUG'] = False
    app.config['SQLALCHEMY_ECHO'] = False

    app.register_blueprint(bp_shutdown)
    app.register_blueprint(auth.bp_auth)
    app.register_blueprint(buyer.bp_buyer)
    app.register_blueprint(seller.bp_seller)
    app.register_blueprint(order.bp_order)

    app.run()
    return app


if __name__ == "__main__":

    app = create_app()
