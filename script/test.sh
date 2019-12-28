#!/bin/sh
export PATHONPATH=`pwd`
coverage run --timid --branch --source fe,be --concurrency=thread -m pytest fe/test/test_add_book.py
coverage combine
coverage report
coverage html -d script/html
