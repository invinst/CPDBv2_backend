#!/usr/bin/env bash
ansible-playbook ansible/staging.yml -i ansible/inventory/staging --vault-password-file ../vault_pass.txt
