#!/usr/bin/env python3
import json
import os
import sys
import time
from typing import Dict, Any

import requests


SESSION = requests.Session()


SUPERSET_URL = os.getenv("SUPERSET_URL", "http://localhost:8088").rstrip("/")
SUPERSET_USER = os.getenv("SUPERSET_USER", "admin")
SUPERSET_PASSWORD = os.getenv("SUPERSET_PASSWORD", "admin")
APP_DB_URI = os.getenv(
    "APP_DB_URI",
    "postgresql+psycopg2://stocksteward:stocksteward@host.docker.internal:5432/stocksteward",
)
DB_NAME = os.getenv("SUPERSET_DB_NAME", "StockSteward")


def _request(method: str, path: str, token: str | None = None, csrf: str | None = None, **kwargs):
    headers = kwargs.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if csrf:
        headers["X-CSRFToken"] = csrf
        headers["Referer"] = SUPERSET_URL
    headers.setdefault("Content-Type", "application/json")
    return SESSION.request(method, f"{SUPERSET_URL}{path}", headers=headers, **kwargs)


def login() -> str:
    payload = {
        "username": SUPERSET_USER,
        "password": SUPERSET_PASSWORD,
        "provider": "db",
        "refresh": True,
    }
    resp = _request("POST", "/api/v1/security/login", json=payload)
    if not resp.ok:
        raise RuntimeError(f"Login failed: {resp.status_code} {resp.text}")
    data = resp.json()
    return data.get("access_token")


def get_csrf(token: str) -> str:
    resp = _request("GET", "/api/v1/security/csrf_token", token=token)
    if not resp.ok:
        raise RuntimeError(f"CSRF fetch failed: {resp.status_code} {resp.text}")
    return resp.json().get("result")


def find_database(token: str) -> Dict[str, Any] | None:
    resp = _request("GET", "/api/v1/database/?page_size=200", token=token)
    if not resp.ok:
        raise RuntimeError(f"Database list failed: {resp.status_code} {resp.text}")
    for item in resp.json().get("result", []):
        if item.get("database_name") == DB_NAME:
            return item
    return None


def create_database(token: str, csrf: str) -> Dict[str, Any]:
    payload = {
        "database_name": DB_NAME,
        "sqlalchemy_uri": APP_DB_URI,
        "expose_in_sqllab": True,
        "allow_ctas": False,
        "allow_cvas": False,
        "allow_dml": False,
        "allow_run_async": True,
        "extra": json.dumps({
            "metadata_params": {},
            "engine_params": {},
            "metadata_cache_timeout": {},
            "schemas_allowed_for_file_upload": [],
        }),
    }
    resp = _request("POST", "/api/v1/database/", token=token, csrf=csrf, json=payload)
    if not resp.ok:
        raise RuntimeError(f"Database create failed: {resp.status_code} {resp.text}")
    return resp.json()


def list_datasets(token: str):
    resp = _request("GET", "/api/v1/dataset/?page_size=500", token=token)
    if not resp.ok:
        raise RuntimeError(f"Dataset list failed: {resp.status_code} {resp.text}")
    return resp.json().get("result", [])


def ensure_dataset(token: str, csrf: str, database_id: int, table_name: str, schema: str = "public") -> Dict[str, Any]:
    for ds in list_datasets(token):
        if ds.get("table_name") == table_name and ds.get("database", {}).get("id") == database_id:
            return ds
    payload = {
        "database": database_id,
        "schema": schema,
        "table_name": table_name,
    }
    resp = _request("POST", "/api/v1/dataset/", token=token, csrf=csrf, json=payload)
    if not resp.ok:
        raise RuntimeError(f"Dataset create failed ({table_name}): {resp.status_code} {resp.text}")
    return resp.json().get("result") or resp.json()


def list_charts(token: str):
    resp = _request("GET", "/api/v1/chart/?page_size=500", token=token)
    if not resp.ok:
        raise RuntimeError(f"Chart list failed: {resp.status_code} {resp.text}")
    return resp.json().get("result", [])


def ensure_chart(token: str, csrf: str, name: str, dataset_id: int, viz_type: str, params: Dict[str, Any]) -> int:
    for chart in list_charts(token):
        if chart.get("slice_name") == name and chart.get("datasource_id") == dataset_id:
            return chart.get("id")
    payload = {
        "slice_name": name,
        "viz_type": viz_type,
        "datasource_id": dataset_id,
        "datasource_type": "table",
        "params": json.dumps(params),
    }
    resp = _request("POST", "/api/v1/chart/", token=token, csrf=csrf, json=payload)
    if not resp.ok:
        raise RuntimeError(f"Chart create failed ({name}): {resp.status_code} {resp.text}")
    return resp.json().get("id") or resp.json().get("result", {}).get("id")


def create_dashboard(token: str, csrf: str, charts: Dict[str, int]) -> str:
    position_json = {
        "DASHBOARD_VERSION_KEY": "v2",
        "ROOT_ID": {"type": "ROOT", "id": "ROOT_ID", "children": ["GRID_ID"]},
        "GRID_ID": {"type": "GRID", "id": "GRID_ID", "children": ["ROW-1"]},
        "ROW-1": {"type": "ROW", "id": "ROW-1", "children": ["CHART-1", "CHART-2", "CHART-3"]},
        "ROW-2": {"type": "ROW", "id": "ROW-2", "children": ["CHART-4", "CHART-5"]},
        "ROW-3": {"type": "ROW", "id": "ROW-3", "children": ["CHART-6"]},
        "ROW-4": {"type": "ROW", "id": "ROW-4", "children": ["CHART-7", "CHART-8", "CHART-9"]},
        "ROW-5": {"type": "ROW", "id": "ROW-5", "children": ["CHART-10", "CHART-11"]},
        "CHART-1": {
            "type": "CHART",
            "id": "CHART-1",
            "children": [],
            "meta": {"chartId": charts["trades"], "width": 4, "height": 10},
        },
        "CHART-2": {
            "type": "CHART",
            "id": "CHART-2",
            "children": [],
            "meta": {"chartId": charts["strategies"], "width": 4, "height": 10},
        },
        "CHART-3": {
            "type": "CHART",
            "id": "CHART-3",
            "children": [],
            "meta": {"chartId": charts["portfolios"], "width": 4, "height": 10},
        },
        "CHART-4": {
            "type": "CHART",
            "id": "CHART-4",
            "children": [],
            "meta": {"chartId": charts["trade_volume"], "width": 6, "height": 12},
        },
        "CHART-5": {
            "type": "CHART",
            "id": "CHART-5",
            "children": [],
            "meta": {"chartId": charts["pnl_trend"], "width": 6, "height": 12},
        },
        "CHART-6": {
            "type": "CHART",
            "id": "CHART-6",
            "children": [],
            "meta": {"chartId": charts["top_strategies"], "width": 12, "height": 12},
        },
        "CHART-7": {
            "type": "CHART",
            "id": "CHART-7",
            "children": [],
            "meta": {"chartId": charts["approvals_status"], "width": 4, "height": 10},
        },
        "CHART-8": {
            "type": "CHART",
            "id": "CHART-8",
            "children": [],
            "meta": {"chartId": charts["approvals_volume"], "width": 4, "height": 10},
        },
        "CHART-9": {
            "type": "CHART",
            "id": "CHART-9",
            "children": [],
            "meta": {"chartId": charts["users_by_role"], "width": 4, "height": 10},
        },
        "CHART-10": {
            "type": "CHART",
            "id": "CHART-10",
            "children": [],
            "meta": {"chartId": charts["audit_actions"], "width": 6, "height": 12},
        },
        "CHART-11": {
            "type": "CHART",
            "id": "CHART-11",
            "children": [],
            "meta": {"chartId": charts["audit_volume"], "width": 6, "height": 12},
        },
    }
    payload = {
        "dashboard_title": "StockSteward Executive Overview",
        "slug": "stocksteward-executive-overview",
        "published": True,
        "position_json": json.dumps(position_json),
        "json_metadata": json.dumps({"native_filter_configuration": []}),
    }
    existing = find_dashboard_by_slug(token, "stocksteward-executive-overview")
    if existing and existing.get("id"):
        dash_id = existing["id"]
        resp = _request("PUT", f"/api/v1/dashboard/{dash_id}", token=token, csrf=csrf, json=payload)
        if not resp.ok:
            raise RuntimeError(f"Dashboard update failed: {resp.status_code} {resp.text}")
        return f"{SUPERSET_URL}/superset/dashboard/{dash_id}/"

    resp = _request("POST", "/api/v1/dashboard/", token=token, csrf=csrf, json=payload)
    if not resp.ok:
        raise RuntimeError(f"Dashboard create failed: {resp.status_code} {resp.text}")
    result = resp.json().get("result") or resp.json()
    dash_id = result.get("id")
    if dash_id:
        return f"{SUPERSET_URL}/superset/dashboard/{dash_id}/"
    return f"{SUPERSET_URL}/superset/dashboard/stocksteward-executive-overview/"


def find_dashboard_by_slug(token: str, slug: str) -> Dict[str, Any] | None:
    resp = _request("GET", "/api/v1/dashboard/?page_size=200", token=token)
    if not resp.ok:
        return None
    for item in resp.json().get("result", []):
        if item.get("slug") == slug:
            return item
    return None


def main() -> None:
    print("[superset] Bootstrapping dashboard...")
    token = login()
    csrf = get_csrf(token)

    db = find_database(token)
    if not db:
        print("[superset] Creating database connection...")
        _ = create_database(token, csrf)
        time.sleep(1)
        db = find_database(token)
    db_id = (db or {}).get("id") or (db or {}).get("result", {}).get("id")
    if not db_id:
        raise RuntimeError("Could not resolve Superset database id")

    datasets = {
        "trades": ensure_dataset(token, csrf, db_id, "trades"),
        "strategies": ensure_dataset(token, csrf, db_id, "strategies"),
        "portfolios": ensure_dataset(token, csrf, db_id, "portfolios"),
        "approvals": ensure_dataset(token, csrf, db_id, "trade_approvals"),
        "users": ensure_dataset(token, csrf, db_id, "users"),
        "audit_logs": ensure_dataset(token, csrf, db_id, "audit_logs"),
    }

    charts = {
        "trades": ensure_chart(
            token,
            csrf,
            "Trades by Status",
            datasets["trades"]["id"],
            "table",
            {
                "query_mode": "aggregate",
                "groupby": ["status"],
                "metrics": ["count"],
                "row_limit": 50,
                "show_cell_bars": False,
            },
        ),
        "strategies": ensure_chart(
            token,
            csrf,
            "Strategies by Status",
            datasets["strategies"]["id"],
            "table",
            {
                "query_mode": "aggregate",
                "groupby": ["status"],
                "metrics": ["count"],
                "row_limit": 50,
                "show_cell_bars": False,
            },
        ),
        "portfolios": ensure_chart(
            token,
            csrf,
            "Portfolio Snapshot",
            datasets["portfolios"]["id"],
            "table",
            {
                "query_mode": "raw",
                "all_columns": ["name", "invested_amount", "cash_balance", "win_rate"],
                "row_limit": 50,
            },
        ),
        "trade_volume": ensure_chart(
            token,
            csrf,
            "Trade Volume Trend",
            datasets["trades"]["id"],
            "echarts_timeseries",
            {
                "time_range": "Last 30 days",
                "granularity_sqla": "timestamp",
                "metrics": [
                    {
                        "expressionType": "SQL",
                        "sqlExpression": "SUM(price * quantity)",
                        "label": "Notional Volume",
                    }
                ],
                "groupby": [],
                "timeseries_limit": 1000,
                "rolling_type": "None",
            },
        ),
        "pnl_trend": ensure_chart(
            token,
            csrf,
            "PnL Trend (Trades)",
            datasets["trades"]["id"],
            "echarts_timeseries",
            {
                "time_range": "Last 30 days",
                "granularity_sqla": "timestamp",
                "metrics": [
                    {
                        "expressionType": "SQL",
                        "sqlExpression": "AVG(NULLIF(REPLACE(pnl, '%', ''), '')::float)",
                        "label": "Avg PnL %",
                    }
                ],
                "groupby": [],
                "timeseries_limit": 1000,
                "rolling_type": "None",
            },
        ),
        "top_strategies": ensure_chart(
            token,
            csrf,
            "Top Strategies by PnL",
            datasets["strategies"]["id"],
            "table",
            {
                "query_mode": "raw",
                "all_columns": ["name", "symbol", "status", "pnl", "drawdown"],
                "order_by_cols": ["pnl"],
                "row_limit": 20,
            },
        ),
        "approvals_status": ensure_chart(
            token,
            csrf,
            "Trade Approvals by Status",
            datasets["approvals"]["id"],
            "table",
            {
                "query_mode": "aggregate",
                "groupby": ["status"],
                "metrics": ["count"],
                "row_limit": 50,
            },
        ),
        "approvals_volume": ensure_chart(
            token,
            csrf,
            "Approval Requests Over Time",
            datasets["approvals"]["id"],
            "echarts_timeseries",
            {
                "time_range": "Last 30 days",
                "granularity_sqla": "created_at",
                "metrics": ["count"],
                "groupby": [],
                "timeseries_limit": 1000,
                "rolling_type": "None",
            },
        ),
        "users_by_role": ensure_chart(
            token,
            csrf,
            "Users by Role",
            datasets["users"]["id"],
            "table",
            {
                "query_mode": "aggregate",
                "groupby": ["role"],
                "metrics": ["count"],
                "row_limit": 50,
            },
        ),
        "audit_actions": ensure_chart(
            token,
            csrf,
            "Audit Actions by Type",
            datasets["audit_logs"]["id"],
            "table",
            {
                "query_mode": "aggregate",
                "groupby": ["action"],
                "metrics": ["count"],
                "row_limit": 100,
            },
        ),
        "audit_volume": ensure_chart(
            token,
            csrf,
            "Audit Events Over Time",
            datasets["audit_logs"]["id"],
            "echarts_timeseries",
            {
                "time_range": "Last 30 days",
                "granularity_sqla": "timestamp",
                "metrics": ["count"],
                "groupby": [],
                "timeseries_limit": 1000,
                "rolling_type": "None",
            },
        ),
    }

    url = create_dashboard(token, csrf, charts)
    print(f"[superset] Dashboard ready: {url}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[superset] ERROR: {exc}")
        sys.exit(1)
