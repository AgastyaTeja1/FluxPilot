# serving/metrics.py

from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response, Request
from starlette.middleware.base import BaseHTTPMiddleware

# Metrics definitions
REQUEST_COUNT = Counter(
    "fluxpilot_http_requests_total",
    "Total HTTP requests processed",
    ["method", "endpoint", "http_status"]
)
REQUEST_LATENCY = Histogram(
    "fluxpilot_http_request_latency_seconds",
    "Latency of HTTP requests in seconds",
    ["method", "endpoint"]
)

class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Starlette middleware to record Prometheus metrics for each request.
    """
    async def dispatch(self, request: Request, call_next):
        method = request.method
        endpoint = request.url.path
        # Measure latency
        with REQUEST_LATENCY.labels(method=method, endpoint=endpoint).time():
            response = await call_next(request)
        status = response.status_code
        # Count request
        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            http_status=status
        ).inc()
        return response

def metrics_endpoint():
    """
    FastAPI route handler to expose metrics in Prometheus format.
    """
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
