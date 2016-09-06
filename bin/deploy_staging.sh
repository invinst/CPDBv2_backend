#!/usr/bin/env bash

ansible-playbook ansible/staging.yml -i ansible/inventory/staging --tags "${1:-deploy}" --ask-vault-pass --ask-pass
