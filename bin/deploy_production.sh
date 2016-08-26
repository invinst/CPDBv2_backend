#!/usr/bin/env bash

deftags=deploy
ansible-playbook ansible/production.yml -i ansible/inventory/production --tags "${1:$deftags}" --ask-vault-pass --ask-pass
