#!/bin/bash

export PYENV_ROOT="/webapps/pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"

if which pyenv > /dev/null; then eval "$(pyenv init -)"; fi

(pyenv versions | grep "$1") || pyenv install "$1"
