#!/usr/bin/env bash

ansible-playbook ansible/staging.yml -i ansible/inventory/staging --tags "${1:-deploy}" --vault-password-file ../vault_pass.txt
