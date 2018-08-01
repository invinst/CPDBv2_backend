#!/usr/bin/env bash
coverage run ./cpdb/manage.py test && coverage combine && coverage report --omit="/home/ubuntu/virtualenvs/*"
