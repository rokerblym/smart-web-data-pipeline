#!/bin/zsh
set -e

echo "==> Smart Web Data Pipeline setup"

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

[ -f .env ] || cp .env.example .env

docker compose up -d db

for i in {1..40}; do
  docker compose exec -T db pg_isready -U appuser -d webdatadb >/dev/null 2>&1 && break
  sleep 1
done

export DATABASE_URL="postgresql+asyncpg://appuser:apppassword@localhost:5434/webdatadb"

alembic upgrade head
pytest -q

echo ""
echo "READY"
echo "Run: docker compose up --build"
echo "Swagger: http://127.0.0.1:8002/docs"
