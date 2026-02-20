import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.observability.metrics import API_REQUESTS_TOTAL, API_REQUEST_LATENCY_SECONDS


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id
        start = time.perf_counter()

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            status_code = 500
            raise
        finally:
            latency = time.perf_counter() - start
            method = request.method
            path = request.url.path
            API_REQUEST_LATENCY_SECONDS.labels(method=method, path=path).observe(latency)
            API_REQUESTS_TOTAL.labels(method=method, path=path, status=str(status_code)).inc()

        response.headers["x-request-id"] = request_id
        return response

