"""
用户可以通过关键字搜索，参数化的搜索方式；
如搜索范围包括，题目，标签，目录，内容；全站搜索或是当前店铺搜索。
如果显示结果较大，需要分页 (使用全文索引优化查找)
"""
import logging
from flask import jsonify
from flask import Blueprint, request

from app.model.search import SearchMethod

bp_search = Blueprint("search", __name__, url_prefix="/search")

s = SearchMethod()

# 题目确切查询：直接给出"本店/全站"

# 本店模糊查询
@bp_search.route("/store", methods=['POST'])
def search_store():
    keyword = request.json['keyword']
    store_id = request.json['store_id']

    token = "return from function"
    return jsonify({"message": message, "token": token}), code

# 全站模糊查询
@bp_search.route("/all", methods=['POST'])
def search_all():
    keyword = request.json['keyword']

    return jsonify({"message": message, "token": token}), code
