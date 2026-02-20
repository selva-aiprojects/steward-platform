#!/usr/bin/env sh
set -eu

export FLASK_APP=superset

echo "[superset] validating required environment..."
: "${SUPERSET_SECRET_KEY:?SUPERSET_SECRET_KEY is required}"

DB_URL="${SQLALCHEMY_DATABASE_URI:-${DATABASE_URL:-}}"
if [ -z "${DB_URL}" ]; then
  echo "[superset] ERROR: DATABASE_URL / SQLALCHEMY_DATABASE_URI is missing"
  exit 1
fi

echo "[superset] waiting for database connectivity..."
python - <<'PY'
import os, time
from sqlalchemy import create_engine, text

db_url = os.getenv("SQLALCHEMY_DATABASE_URI") or os.getenv("DATABASE_URL")
last_error = None
for attempt in range(1, 61):
    try:
        engine = create_engine(db_url, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"[superset] database reachable on attempt {attempt}")
        raise SystemExit(0)
    except Exception as e:
        last_error = e
        print(f"[superset] db not ready (attempt {attempt}/60): {e}")
        time.sleep(3)

print(f"[superset] ERROR: database never became ready: {last_error}")
raise SystemExit(1)
PY

echo "[superset] running migrations..."
superset db upgrade

echo "[superset] creating admin user (idempotent)..."
superset fab create-admin \
  --username "${SUPERSET_ADMIN_USERNAME:-admin}" \
  --firstname "${SUPERSET_ADMIN_FIRSTNAME:-StockSteward}" \
  --lastname "${SUPERSET_ADMIN_LASTNAME:-Admin}" \
  --email "${SUPERSET_ADMIN_EMAIL:-admin@stocksteward.local}" \
  --password "${SUPERSET_ADMIN_PASSWORD:-admin}" || true

echo "[superset] initializing superset..."
superset init

echo "[superset] starting web server..."
exec gunicorn \
  --bind "0.0.0.0:${PORT:-8088}" \
  --workers 2 \
  --worker-class gevent \
  --timeout 120 \
  "superset.app:create_app()"