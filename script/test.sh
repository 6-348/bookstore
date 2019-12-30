#!/bin/sh
export PATHONPATH=`pwd`
coverage run --timid --branch --source fe,be,app --concurrency=thread -m pytest -v --ignore=fe/data
coverage combine
coverage report
coverage html -d script/html
