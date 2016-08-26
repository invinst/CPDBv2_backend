#!/usr/bin/env bash

deftags=deploy
ansible-playbook ansible/staging.yml -i ansible/inventory/staging --tags "${1:$deftags}" --ask-vault-pass --ask-pass
