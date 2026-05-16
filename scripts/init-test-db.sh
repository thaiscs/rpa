#!/bin/bash
set -e

# Create test database only if it does not already exist
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    SELECT 'CREATE DATABASE certsdb_test'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'certsdb_test')\gexec
EOSQL

echo "Test database ready."
