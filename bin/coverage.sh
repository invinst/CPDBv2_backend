#!/usr/bin/env bash
coverage run ./cpdb/manage.py test && coverage report -m cpdb/**/*.py && coverage html
