#!/usr/bin/env bash
ansible-playbook ansible/staging.yml -i ansible/inventory/staging --ask-vault-pass --ask-pass
