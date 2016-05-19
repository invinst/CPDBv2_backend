#!/usr/bin/bash
ansible-playbook ansible/staging.yml -i ansible/inventory/staging --tags "deploy" --ask-vault-pass --ask-pass
