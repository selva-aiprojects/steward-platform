# Render Deployment: Observability + Superset

This repo now includes a Render Blueprint at `render.yaml` for:

- `stocksteward-superset` (Superset web app)
- `stocksteward-prometheus` (Prometheus scraper)
- `stocksteward-superset-redis` (Redis)
- `stocksteward-superset-db` (Postgres)

## 1. Create services from Blueprint

1. Push current branch to your Git repo.
2. In Render dashboard: New -> Blueprint.
3. Select this repo/branch.
4. Render will parse `render.yaml` and show all services.
5. Create the stack.

## 2. Required environment values

In `stocksteward-prometheus` service:

- `BACKEND_TARGET`: set to your backend Render hostname
  - Example: `stocksteward-backend.onrender.com`
- `METRICS_USER_ID`: superadmin user id from backend DB
  - Example: `999`

`METRICS_USER_ROLE` defaults to `SUPERADMIN`.

## 3. Superadmin-only metrics

Prometheus scrapes:

- `/api/v1/logs/metrics`

This endpoint is superadmin-only. Ensure the `METRICS_USER_ID` belongs to a valid superadmin user.

## 4. Superset first login

Superset admin credentials are created from env vars:

- `SUPERSET_ADMIN_USERNAME`
- `SUPERSET_ADMIN_PASSWORD`

Both are configured in the Blueprint (password generated automatically).

## 5. Notes

- Render may warn that `version` in Docker Compose is obsolete; this is unrelated to Blueprint deployment.
- Prometheus service in this setup is private monitoring infra; expose only if needed.
- You can connect Superset to your main app database to build business dashboards.

