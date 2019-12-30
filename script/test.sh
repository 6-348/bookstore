#!/bin/sh
export PATHONPATH=`pwd`
<<<<<<< HEAD
coverage run --timid --branch --source fe,be --concurrency=thread -m pytest
=======
coverage run --timid --branch --source fe,be --concurrency=thread -m pytest -v --ignore=fe/data
>>>>>>> 3cbda147243aad6cc52745e6f48a541f8facbf90
coverage combine
coverage report
coverage html -d script/html
