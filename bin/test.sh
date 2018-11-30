#!/usr/bin/env bash

bin/manage.sh --local makemigrations --dry-run && bin/manage.sh --local test $@
