#!/bin/bash
python manage.py makemigrations shub
python manage.py makemigrations users
python manage.py makemigrations main
python manage.py makemigrations
python manage.py migrate auth
python manage.py migrate
python manage.py collectstatic --noinput
python scripts/upload_base_packages.py
uwsgi uwsgi.ini
