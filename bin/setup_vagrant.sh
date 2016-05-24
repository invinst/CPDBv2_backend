#!/usr/bin/env bash
ansible-playbook ansible/vagrant.yml -i ansible/inventory/vagrant --ask-vault-pass --ask-pass
