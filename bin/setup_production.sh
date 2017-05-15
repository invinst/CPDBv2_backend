#!/usr/bin/env bash
ansible-playbook ansible/production.yml -i ansible/inventory/production --vault-password-file ../vault_pass.txt
