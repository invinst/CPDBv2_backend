#!/usr/bin/bash
ansible-playbook ansible/staging.yml -i ansible/inventory/staging --ask-vault-pass --ask-pass

