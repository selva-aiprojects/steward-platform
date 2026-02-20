# Railway Deployment Guide

## Backend (from repo root)

This repo now includes `railway.json` so Railway can deploy backend without setting root directory manually.

- Build command:
  - `cd backend && pip install --no-cache-dir -r requirements.txt`
- Start command:
  - `cd backend && uvicorn app.main:socket_app --host 0.0.0.0 --port $PORT`
- Health check:
  - `/health`

### Required environment variables (backend)

- `DATABASE_URL` (or defaults to local sqlite, not recommended for Railway)
- `APP_ENV=PROD`
- `EXECUTION_MODE=PAPER_TRADING` (or LIVE_TRADING if intentionally enabled)
- `CORS_ORIGINS` as needed
- API keys as required by your features

## Superset on Railway

Create a separate Railway service using Dockerfile:

- Dockerfile path: `infra/render/superset/Dockerfile`

Set env vars:

- `DATABASE_URL` (Superset metadata DB connection string)
- `REDIS_URL`
- `SUPERSET_SECRET_KEY`
- `SUPERSET_ADMIN_USERNAME`
- `SUPERSET_ADMIN_PASSWORD`
- `SUPERSET_ADMIN_EMAIL`

## Prometheus on Railway

Create another Railway service using Dockerfile:

- Dockerfile path: `infra/render/prometheus/Dockerfile`

Set env vars:

- `BACKEND_SCHEME=https`
- `BACKEND_TARGET=<your-backend-host>`
- `METRICS_USER_ID=<superadmin-user-id>`
- `METRICS_USER_ROLE=SUPERADMIN`

Prometheus scrapes backend superadmin-only metrics endpoint:

- `/api/v1/logs/metrics`

## Notes

- Railway may still show the old failure if deployment is retried on an older commit. Redeploy latest commit.
- If deployment uses a different service root override in Railway settings, clear it or keep it consistent.

