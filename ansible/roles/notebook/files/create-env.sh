#!/bin/bash

export PYENV_ROOT="/pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"

if which pyenv > /dev/null; then
    eval "$(pyenv init -)";
    eval "$(pyenv virtualenv-init -)";
fi

(pyenv versions | grep "$2") || pyenv virtualenv $1 $2
