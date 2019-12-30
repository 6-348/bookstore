#!/bin/sh
export PATHONPATH=`pwd`
<<<<<<< HEAD
coverage run --timid --branch --source fe,be --concurrency=thread -m pytest fe/test/test_password.py
=======
coverage run --timid --branch --source fe,be --concurrency=thread -m pytest fe/test/test_my_order.py
>>>>>>> mjy
coverage combine
coverage report
coverage html -d script/html
