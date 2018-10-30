#!/bin/bash
set -e

/docker-entrypoint-initdb.d/copy-certificates.sh
exec /usr/local/bin/docker-entrypoint.sh "$@"
