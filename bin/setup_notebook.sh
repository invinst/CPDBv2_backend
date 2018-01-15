#!/usr/bin/env bash
ansible-playbook ansible/notebook.yml -i ansible/inventory/notebook --vault-password-file ../vault_pass.txt
