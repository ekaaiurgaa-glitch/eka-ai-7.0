"""Monitoring and observability."""
import logging
from typing import Optional
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time

http_requests_total = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
http_request_duration_seconds = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
ai_requests_total = Counter('ai_requests_total', 'Total AI requests', ['model', 'status'])
ai_request_duration_seconds = Histogram('ai_request_duration_seconds', 'AI request duration', ['model'])

logger = logging.getLogger(__name__)


class MonitoringMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start_time = time.time()
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                duration = time.time() - start_time
                http_requests_total.labels(method=scope["method"], endpoint=scope["path"], status=message["status"]).inc()
                http_request_duration_seconds.labels(method=scope["method"], endpoint=scope["path"]).observe(duration)
            await send(message)
        
        await self.app(scope, receive, send_wrapper)


def setup_sentry(dsn: Optional[str] = None):
    if not dsn:
        return
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        sentry_sdk.init(dsn=dsn, traces_sample_rate=0.1, integrations=[FastApiIntegration()])
        logger.info("Sentry initialized")
    except ImportError:
        logger.warning("Sentry SDK not installed")


async def metrics_endpoint(request):
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
