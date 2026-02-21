from fastapi import APIRouter, HTTPException, Depends, Response
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from prometheus_client.parser import text_string_to_metric_families
from app.core.rbac import get_current_user
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.observability.metrics import (
    update_market_metrics,
    update_strategy_metrics,
    update_portfolio_metrics,
    update_trade_metrics,
    update_user_metrics,
)
from app.models.user import User

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("frontend_errors")

class ErrorLog(BaseModel):
    level: str
    message: str
    context: Optional[Dict[str, Any]] = None
    source: str

@router.post("/error")
def log_frontend_error(error: ErrorLog):
    """
    Log critical frontend errors to the backend system.
    """
    if error.level == "CRITICAL":
        logger.critical(f"FRONTEND CRASH: {error.message} | Context: {error.context}")
    else:
        logger.error(f"Frontend Error: {error.message}")
    
    # In a real system, we would insert this into an 'error_logs' table in DB
    
    return {"status": "logged", "level": error.level}


@router.get("/metrics")
def get_metrics(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Superadmin-only Prometheus metrics endpoint.
    """
    if current_user.role != "SUPERADMIN" and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Insufficient privileges")
    update_market_metrics()
    update_strategy_metrics(db)
    update_portfolio_metrics(db)
    update_trade_metrics(db)
    update_user_metrics(db)
    payload = generate_latest()
    return Response(content=payload, media_type=CONTENT_TYPE_LATEST)


@router.get("/metrics/summary")
def get_metrics_summary(current_user: User = Depends(get_current_user)):
    """
    Superadmin-only, human-friendly observability summary.
    """
    if current_user.role != "SUPERADMIN" and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Insufficient privileges")

    raw = generate_latest().decode("utf-8")
    families = list(text_string_to_metric_families(raw))

    request_total = 0.0
    request_by_path: Dict[str, float] = {}
    latency_sum_by_path: Dict[str, float] = {}
    latency_count_by_path: Dict[str, float] = {}

    provider_calls: Dict[str, float] = {}
    provider_failures: Dict[str, float] = {}
    provider_latency_sum: Dict[str, float] = {}
    provider_latency_count: Dict[str, float] = {}

    strategy_updates_success = 0.0
    strategy_updates_failure = 0.0

    for family in families:
        if family.name == "stocksteward_api_requests_total":
            for sample in family.samples:
                labels = sample.labels or {}
                path = labels.get("path", "unknown")
                value = float(sample.value or 0.0)
                request_total += value
                request_by_path[path] = request_by_path.get(path, 0.0) + value

        elif family.name == "stocksteward_api_request_latency_seconds_sum":
            for sample in family.samples:
                path = (sample.labels or {}).get("path", "unknown")
                latency_sum_by_path[path] = latency_sum_by_path.get(path, 0.0) + float(sample.value or 0.0)

        elif family.name == "stocksteward_api_request_latency_seconds_count":
            for sample in family.samples:
                path = (sample.labels or {}).get("path", "unknown")
                latency_count_by_path[path] = latency_count_by_path.get(path, 0.0) + float(sample.value or 0.0)

        elif family.name == "stocksteward_external_calls_total":
            for sample in family.samples:
                labels = sample.labels or {}
                provider = labels.get("provider", "unknown")
                status = labels.get("status", "success")
                value = float(sample.value or 0.0)
                provider_calls[provider] = provider_calls.get(provider, 0.0) + value
                if status == "failure":
                    provider_failures[provider] = provider_failures.get(provider, 0.0) + value

        elif family.name == "stocksteward_external_call_latency_seconds_sum":
            for sample in family.samples:
                provider = (sample.labels or {}).get("provider", "unknown")
                provider_latency_sum[provider] = provider_latency_sum.get(provider, 0.0) + float(sample.value or 0.0)

        elif family.name == "stocksteward_external_call_latency_seconds_count":
            for sample in family.samples:
                provider = (sample.labels or {}).get("provider", "unknown")
                provider_latency_count[provider] = provider_latency_count.get(provider, 0.0) + float(sample.value or 0.0)

        elif family.name == "stocksteward_llm_strategy_updates_total":
            for sample in family.samples:
                status = (sample.labels or {}).get("status", "success")
                value = float(sample.value or 0.0)
                if status == "success":
                    strategy_updates_success += value
                else:
                    strategy_updates_failure += value

    top_paths = []
    for path, count in sorted(request_by_path.items(), key=lambda x: x[1], reverse=True)[:8]:
        c = latency_count_by_path.get(path, 0.0)
        s = latency_sum_by_path.get(path, 0.0)
        avg_ms = (s / c * 1000.0) if c > 0 else 0.0
        top_paths.append({
            "path": path,
            "requests": int(count),
            "avg_latency_ms": round(avg_ms, 2),
        })

    providers = []
    for provider, total in sorted(provider_calls.items(), key=lambda x: x[1], reverse=True):
        failures = provider_failures.get(provider, 0.0)
        failure_rate = (failures / total) if total > 0 else 0.0
        c = provider_latency_count.get(provider, 0.0)
        s = provider_latency_sum.get(provider, 0.0)
        avg_ms = (s / c * 1000.0) if c > 0 else 0.0
        health = "HEALTHY"
        if failure_rate >= 0.1:
            health = "DEGRADED"
        if failure_rate >= 0.25:
            health = "CRITICAL"
        providers.append({
            "provider": provider,
            "calls": int(total),
            "failure_rate_pct": round(failure_rate * 100.0, 2),
            "avg_latency_ms": round(avg_ms, 2),
            "health": health,
        })

    total_strategy_updates = strategy_updates_success + strategy_updates_failure
    strategy_success_rate = (strategy_updates_success / total_strategy_updates) if total_strategy_updates > 0 else 0.0

    overall_status = "HEALTHY"
    global_failure_rate = (
        sum(provider_failures.values()) / sum(provider_calls.values())
        if sum(provider_calls.values()) > 0
        else 0.0
    )
    if global_failure_rate >= 0.1:
        overall_status = "DEGRADED"
    if global_failure_rate >= 0.25:
        overall_status = "CRITICAL"

    return {
        "overall_status": overall_status,
        "headline": {
            "total_requests": int(request_total),
            "external_failure_rate_pct": round(global_failure_rate * 100.0, 2),
            "strategy_update_success_rate_pct": round(strategy_success_rate * 100.0, 2),
        },
        "traffic_summary": {
            "top_endpoints": top_paths,
        },
        "provider_summary": providers,
        "strategy_updates": {
            "success": int(strategy_updates_success),
            "failed": int(strategy_updates_failure),
        },
        "advice": [
            "If provider failure rate exceeds 5%, switch to stale-cache-first mode and investigate upstream API limits.",
            "If average latency on /api/v1/market/movers exceeds 1500ms, reduce fallback timeout budget further.",
            "Track strategy update failures; if non-zero, inspect DB write path and user strategy availability."
        ],
    }
