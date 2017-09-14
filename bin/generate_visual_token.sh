#!/usr/bin/env bash

set -e
source /pyenv/versions/cpdb/bin/activate

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd $DIR/..

cpdb/manage.py generate_visual_tokens
optipng $VISUAL_TOKEN_MEDIA_PATH*.png
azcopy \
  --quiet \
  --source $VISUAL_TOKEN_MEDIA_PATH \
  --destination https://$VISUAL_TOKEN_STORAGEACCOUNTNAME.blob.core.windows.net/visual-token \
  --dest-key $VISUAL_TOKEN_STORAGEACCOUNTKEY
