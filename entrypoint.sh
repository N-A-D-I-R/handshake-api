#!/bin/bash
set -e

echo "Waiting for postgres..."

until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER"; do
  sleep 1
done

echo "PostgreSQL started"

alembic upgrade head

exec uvicorn main:app --host 0.0.0.0 --port 8000