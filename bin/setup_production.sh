#!/usr/bin/env bash
ansible-playbook ansible/production.yml -i ansible/inventory/production --ask-vault-pass --ask-pass
