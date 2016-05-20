#!/usr/bin/bash
ansible-playbook ansible/production.yml -i ansible/inventory/production --tags "deploy" --ask-vault-pass --ask-pass
