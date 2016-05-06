#!/bin/bash

export PYENV_ROOT="/webapps/pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"

if which pyenv > /dev/null; then
    eval "$(pyenv init -)";
    eval "$(pyenv virtualenv-init -)";
fi

pyenv virtualenv $1 $2 $3
