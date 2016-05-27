#!/usr/bin/env bash
ansible-playbook ansible/production.yml -i ansible/inventory/production --tags "deploy" --ask-vault-pass --ask-pass
