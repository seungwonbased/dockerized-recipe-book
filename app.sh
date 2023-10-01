#!/bin/bash

flask db init
flask db migrate
flask db upgrade

gunicorn --bind 0.0.0.0:5000 --timeout 90 "app:create_app()"
