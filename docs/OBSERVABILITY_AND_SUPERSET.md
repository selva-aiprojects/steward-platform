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

## Superadmin Observability Portal (In-App)

Open:
- `http://localhost:3000/admin/observability`

This page embeds Grafana (live system pulse) and Superset (business intelligence) for superadmin users.

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

## Grafana Superadmin Dashboard (Auto Provisioned)

Grafana auto-loads a dashboard named **Superadmin Observability** from:
- `infra/observability/grafana/dashboards/superadmin.json`

## Superadmin: Market + Strategy Realtime Panels

5. Market movers (top change % by bucket):
```promql
topk(5, stocksteward_market_mover_change_pct{bucket="gainers"})
```
```promql
bottomk(5, stocksteward_market_mover_change_pct{bucket="losers"})
```

6. Market mover prices:
```promql
stocksteward_market_mover_price
```

7. Market data source status (1 = active):
```promql
stocksteward_market_source_status
```

8. Macro indicators:
```promql
stocksteward_macro_indicator
```

9. Strategies by status:
```promql
stocksteward_strategy_count
```

10. Strategy PnL % by strategy:
```promql
stocksteward_strategy_pnl_pct
```

11. Average strategy PnL % by status:
```promql
stocksteward_strategy_avg_pnl_pct
```

12. Portfolio cash/invested/win-rate:
```promql
stocksteward_portfolio_cash_balance
```
```promql
stocksteward_portfolio_invested_amount
```
```promql
stocksteward_portfolio_win_rate
```

13. Holdings PnL:
```promql
stocksteward_holding_pnl
```
```promql
stocksteward_holding_pnl_pct
```

14. Trade flow:
```promql
stocksteward_trade_count
```
```promql
stocksteward_trade_count_recent
```

15. Trader/portfolio coverage:
```promql
stocksteward_user_count
```
```promql
stocksteward_portfolio_count
```
```promql
stocksteward_holding_count
```

16. Trade volume and average price:
```promql
stocksteward_trade_volume_recent
```
```promql
stocksteward_trade_avg_price_recent
```

17. Total strategy/trade counts:
```promql
stocksteward_strategy_total
```
```promql
stocksteward_trade_total
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

## Demo Data Generator (More Traders + Investments)

If you want richer dashboards quickly, run:
```bash
docker exec -i stocksteward-ai-backend-1 python /app/scripts/generate_demo_data.py
```

This will add more traders, portfolios, holdings, strategies, and trades without deleting existing data.

## Superset Dashboard Bootstrap (Automatic)

Run once to create a Superset dashboard connected to your app database:
```bash
docker exec -i stocksteward-ai-backend-1 python /app/scripts/bootstrap_superset_dashboard.py
```

This creates:
- Database connection in Superset (`StockSteward`)
- Datasets for `trades`, `strategies`, `portfolios`
- Dashboard: **StockSteward Executive Overview**

## Quick Bootstrap Helper

If Superset is running in Docker and your app database is reachable, run:
```bash
docker exec -i stocksteward-ai-backend-1 \
  env APP_DB_URI=postgresql+psycopg2://stocksteward:stocksteward@host.docker.internal:5432/stocksteward \
  python /app/scripts/bootstrap_superset_dashboard.py
```

Extra datasets now included:
- `trade_approvals`, `users`, `audit_logs`

## Production Embed Gate

To lock Superset embeds behind backend session validation:
1. Set `SUPERSET_EMBED_URL` in backend environment.
2. Ensure only superadmin users can access `/api/v1/admin/observability/embed-url`.
3. Frontend will request the embed URL from backend (no hardcoded URL needed).

## Tooling advice

- Use Grafana + Prometheus for runtime health, SLOs, incident response.
- Use Superset for business intelligence and historical SQL exploration.
- If you want traces next, add OpenTelemetry (FastAPI + SQLAlchemy + httpx exporters).
By default, the scrape config uses `user_id=999` (superadmin) in DEV.

Manual check:
```bash
curl "http://localhost:8000/api/v1/logs/metrics?user_id=999"
```
