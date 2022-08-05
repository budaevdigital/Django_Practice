#!/bin/bash
set -e

# psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$DB_NAME" <<-EOSQL
psql -v ON_ERROR_STOP=1 -U postgres <<-EOSQL
	CREATE USER yatube_user WITH ENCRYPTED PASSWORD '$POSTGRES_PASSWORD';
	CREATE DATABASE yatube;
	GRANT ALL PRIVILEGES ON DATABASE yatube TO yatube_user;
EOSQL