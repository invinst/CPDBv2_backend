#!/usr/bin/env bash
docker-compose run web sh -c "cpdb/manage.py makemigrations --dry-run && python -m lambda.test && coverage run cpdb/manage.py test && coverage report && coverage html"
