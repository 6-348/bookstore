#!/bin/sh
export PATHONPATH=`pwd`
<<<<<<< HEAD
coverage run --timid --branch --source fe,be --concurrency=thread -m pytest  fe/test/test_confirm.py
=======
coverage run --timid --branch --source fe,be --concurrency=thread -m pytest fe/test/test_add_book.py
>>>>>>> 390b46e56a50932af067b68e0f0ed6c9fc135ecd
coverage combine
coverage report
coverage html -d script/html
