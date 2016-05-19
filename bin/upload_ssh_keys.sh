#!/usr/bin/bash
scp ~/.ssh/$1 $2@$3:~/.ssh/id_rsa
scp ~/.ssh/$1.pub $2@$3:~/.ssh/id_rsa.pub
