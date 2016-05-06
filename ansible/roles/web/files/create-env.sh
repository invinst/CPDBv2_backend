#!/bin/bash

export PYENV_ROOT="/webapps/pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"

if which pyenv > /dev/null; then
    eval "$(pyenv init -)";
    eval "$(pyenv virtualenv-init -)";
fi

(pyenv versions | grep "$1") || (test -n $2) || pyenv virtualenv -p $1 $2
