#!/usr/bin/bash
ansible-playbook ansible/production.yml -i ansible/inventory/prodcution--ask-vault-pass --ask-pass
