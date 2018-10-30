#!/bin/bash
set -e

if [ -f /tls-secrets/tls.crt ]; then
  cat /tls-secrets/tls.crt > /var/lib/postgresql/ssl/server.crt
  cat /tls-secrets/tls.key > /var/lib/postgresql/ssl/server.key
  chmod 0600 /var/lib/postgresql/ssl/server.crt
  chmod 0600 /var/lib/postgresql/ssl/server.key
  chown postgres /var/lib/postgresql/ssl/server.crt
  chown postgres /var/lib/postgresql/ssl/server.key
fi
