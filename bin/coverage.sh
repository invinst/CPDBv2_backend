#!/usr/bin/env bash
coverage run ./cpdb/manage.py test && coverage report --omit="/home/ubuntu/virtualenvs/*" && coverage html
