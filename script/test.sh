#!/bin/sh
export PATHONPATH=`pwd`
coverage run --timid --branch --source fe,be --concurrency=thread -m pytest fe/test/test_payment.py
coverage combine
coverage report
coverage html -d script/html
