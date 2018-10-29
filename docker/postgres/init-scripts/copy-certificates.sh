#!/bin/bash
set -e

mkdir -p /var/lib/postgresql/ssl

cat /tls-secrets/tls.crt > /var/lib/postgresql/ssl/server.crt;
cat /tls-secrets/tls.key > /var/lib/postgresql/ssl/server.key;

chmod 0600 /var/lib/postgresql/ssl/server.crt;
chmod 0600 /var/lib/postgresql/ssl/server.key;
