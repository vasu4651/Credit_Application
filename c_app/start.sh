#!/bin/bash 

python manage.py makemigrations --no-input
python manage.py makemigrations myapp --no-input
python manage.py migrate --no-input

python manage.py runserver 0.0.0.0:8000