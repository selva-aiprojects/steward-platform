# Deployment Plan: StockSteward AI

This document outlines the deployment strategy for the StockSteward AI platform, including the application core and the observability stack.

## Target Architecture

The application is designed for a hybrid deployment:
- **Core Application**: Render (FastAPI Backend + React Frontend)
- **Database**: Railway (PostgreSQL) or Neon
- **Observability**: Docker-based stack (Prometheus, Grafana, Superset) deployed on a dedicated VPS or Railway.

---

## 1. Core Application (Render)

### Backend (Web Service)
- **Environment Variables**:
  - `APP_ENV`: `PROD`
  - `DATABASE_URL`: Your Railway/Neon connection string.
  - `GROQ_API_KEY`: Required for AI analysis.
  - `TRUEDATA_API_KEY`: Required for live market data.
- **Build Command**: `cd backend && pip install -r requirements.txt`
- **Start Command**: `cd backend && gunicorn app.main:app -k uvicorn.workers.UvicornWorker`

### Frontend (Static Site)
- **Environment Variables**:
  - `REACT_APP_API_URL`: Your Render backend URL.
  - `REACT_APP_GRAFANA_URL`: URL of your deployed Grafana instance.
  - `REACT_APP_SUPERSET_URL`: URL of your deployed Superset instance.
- **Build Command**: `cd frontend && npm install && npm run build`
- **Publish Directory**: `frontend/dist` (or `build`)

---

## 2. Observability Stack (Railway / Docker VPS)

### Prometheus
- Deploy via `infra/observability/docker-compose.observability.yml`.
- **Target Configuration**: Ensure `prometheus.yml` points to the Render backend metrics endpoint.
  - Use an internal service name or public URL with the `user_id=999` query param (ensure RBAC allows this).

### Grafana
- Deploy alongside Prometheus.
- **Provisioning**: Dashboards located in `infra/observability/grafana/dashboards` are pre-configured for the StockSteward metrics.

### Superset
- Use the custom `infra/render/superset/Dockerfile`.
- Requires a dedicated PostgreSQL database for Superset metadata.
- **Embedding**: Use `SUPERSET_EMBED_URL` in the frontend to show executive reports.

---

## 3. Scaling & Monitoring
- **Vertical Scaling**: Render's Background Workers for long-running market feeds.
- **Database Migration**: Use `alembic` (not included in this setup, but recommended for production).
- **Health Checks**: Monitor `/health` on backend and `/api/v1/logs/metrics` for telemetry.

---

## Verification Checklist
- [/] Backend `/health` returns "ok".
- [/] Frontend loads dashboard with live market data.
- [/] Prometheus scrapes `/api/v1/logs/metrics?user_id=999`.
- [/] Grafana shows data on the "Executive Overview" dashboard.
