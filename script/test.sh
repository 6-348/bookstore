#!/bin/sh
export PATHONPATH=`pwd`
<<<<<<< HEAD
coverage run --timid --branch --source fe,be --concurrency=thread -m pytest fe/test/test_add_book.py
=======
coverage run --timid --branch --source fe,be --concurrency=thread -m pytest  fe/test/test_confirm.py
>>>>>>> origin/mjy
coverage combine
coverage report
coverage html -d script/html
