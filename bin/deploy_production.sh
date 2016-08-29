#!/usr/bin/env bash

ansible-playbook ansible/production.yml -i ansible/inventory/production --tags "${1:-deploy}" --ask-vault-pass --ask-pass
