# Observability and Visualization Setup

## What is now instrumented

- Request-level metrics:
  - `stocksteward_api_requests_total`
  - `stocksteward_api_request_latency_seconds`
- External provider metrics (Kite, Yahoo, LLM providers):
  - `stocksteward_external_calls_total`
  - `stocksteward_external_call_latency_seconds`
- LLM-driven strategy update metric:
  - `stocksteward_llm_strategy_updates_total`
- Request correlation:
  - Every HTTP response now includes `x-request-id`.

Metrics endpoint (superadmin-only):
- `GET /api/v1/logs/metrics`

## Start backend

Run backend normally (must be reachable at `http://localhost:8000`).

## Start Prometheus, Grafana, Superset

From repo root:

```bash
docker compose -f infra/observability/docker-compose.observability.yml up -d
```

URLs:
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3001` (`admin` / `admin`)
- Superset: `http://localhost:8088` (`admin` / `admin`)

## Prometheus notes

Config file:
- `infra/observability/prometheus.yml`

Alert rules:
- `infra/observability/alert_rules.yml`

## Suggested Grafana panels

1. API p95 latency:
```promql
histogram_quantile(0.95, sum(rate(stocksteward_api_request_latency_seconds_bucket[5m])) by (le, path))
```

2. External provider failure rate:
```promql
sum(rate(stocksteward_external_calls_total{status="failure"}[5m])) / clamp_min(sum(rate(stocksteward_external_calls_total[5m])), 1)
```

3. External call latency by provider:
```promql
histogram_quantile(0.95, sum(rate(stocksteward_external_call_latency_seconds_bucket[5m])) by (le, provider))
```

4. LLM strategy update success/failure:
```promql
sum by (status) (increase(stocksteward_llm_strategy_updates_total[1h]))
```

## Apache Superset usage

Superset is best for product/ops analytics from SQL tables rather than Prometheus time-series.

Recommended:
1. Add your application database as a Superset data source.
2. Build charts for:
   - trade volume per day
   - strategy PnL trend
   - approval funnel
   - optimization results over time
3. Combine Superset (business analytics) with Grafana (runtime/infra observability).

## Tooling advice

- Use Grafana + Prometheus for runtime health, SLOs, incident response.
- Use Superset for business intelligence and historical SQL exploration.
- If you want traces next, add OpenTelemetry (FastAPI + SQLAlchemy + httpx exporters).
By default, the scrape config uses `user_id=999` (superadmin) in DEV.

Manual check:
```bash
curl "http://localhost:8000/api/v1/logs/metrics?user_id=999"
```

