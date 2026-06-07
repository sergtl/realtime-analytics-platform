#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
COMPOSE_FILE="$API_DIR/docker-compose.test.yml"

cleanup() {
    docker compose -f "$COMPOSE_FILE" down -v
}

trap cleanup EXIT

cleanup
docker compose -f "$COMPOSE_FILE" up -d

until docker compose -f "$COMPOSE_FILE" exec -T postgres pg_isready -U sergei -d rpap_test; do
    sleep 1
done

until docker compose -f "$COMPOSE_FILE" exec -T redis redis-cli ping; do
    sleep 1
done

export DATABASE_URL="postgresql+psycopg://sergei:postgres@localhost:5433/rpap_test"
export REDIS_URL="redis://localhost:6380/0"
export DEBUG=false

cd "$API_DIR"

uv run alembic upgrade head
uv run pytest "$@"
