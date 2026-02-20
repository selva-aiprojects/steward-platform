#!/usr/bin/env sh
set -eu

export FLASK_APP=superset

superset db upgrade

superset fab create-admin \
  --username "${SUPERSET_ADMIN_USERNAME:-admin}" \
  --firstname "${SUPERSET_ADMIN_FIRSTNAME:-StockSteward}" \
  --lastname "${SUPERSET_ADMIN_LASTNAME:-Admin}" \
  --email "${SUPERSET_ADMIN_EMAIL:-admin@stocksteward.local}" \
  --password "${SUPERSET_ADMIN_PASSWORD:-admin}" || true

superset init

# Use Render-provided PORT.
exec superset run -h 0.0.0.0 -p "${PORT:-8088}"