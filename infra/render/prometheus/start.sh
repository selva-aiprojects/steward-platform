#!/bin/sh
set -eu

BACKEND_SCHEME="${BACKEND_SCHEME:-https}"
BACKEND_TARGET="${BACKEND_TARGET:-stocksteward-ai.onrender.com}"
METRICS_USER_ID="${METRICS_USER_ID:-999}"
METRICS_USER_ROLE="${METRICS_USER_ROLE:-SUPERADMIN}"

sed \
  -e "s|__BACKEND_SCHEME__|${BACKEND_SCHEME}|g" \
  -e "s|__BACKEND_TARGET__|${BACKEND_TARGET}|g" \
  -e "s|__METRICS_USER_ID__|${METRICS_USER_ID}|g" \
  -e "s|__METRICS_USER_ROLE__|${METRICS_USER_ROLE}|g" \
  /etc/prometheus/prometheus.tmpl.yml > /etc/prometheus/prometheus.yml

exec /bin/prometheus \
  --config.file=/etc/prometheus/prometheus.yml \
  --storage.tsdb.path=/prometheus \
  --web.listen-address=0.0.0.0:${PORT:-9090}