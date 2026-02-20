from prometheus_client import Counter, Histogram


API_REQUESTS_TOTAL = Counter(
    "stocksteward_api_requests_total",
    "Total API requests",
    ["method", "path", "status"],
)

API_REQUEST_LATENCY_SECONDS = Histogram(
    "stocksteward_api_request_latency_seconds",
    "API request latency in seconds",
    ["method", "path"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 3, 5, 8, 13, 21),
)

EXTERNAL_CALLS_TOTAL = Counter(
    "stocksteward_external_calls_total",
    "External provider calls",
    ["provider", "operation", "status"],
)

EXTERNAL_CALL_LATENCY_SECONDS = Histogram(
    "stocksteward_external_call_latency_seconds",
    "External provider latency in seconds",
    ["provider", "operation"],
    buckets=(0.02, 0.05, 0.1, 0.2, 0.35, 0.5, 0.75, 1, 2, 3, 5, 8, 13),
)

LLM_STRATEGY_UPDATES_TOTAL = Counter(
    "stocksteward_llm_strategy_updates_total",
    "LLM-triggered strategy updates",
    ["status"],
)


def record_external_call(provider: str, operation: str, latency_seconds: float | None, success: bool) -> None:
    status = "success" if success else "failure"
    EXTERNAL_CALLS_TOTAL.labels(provider=provider, operation=operation, status=status).inc()
    if latency_seconds is not None:
        EXTERNAL_CALL_LATENCY_SECONDS.labels(provider=provider, operation=operation).observe(max(latency_seconds, 0.0))


def record_strategy_update(success: bool) -> None:
    LLM_STRATEGY_UPDATES_TOTAL.labels(status="success" if success else "failure").inc()

