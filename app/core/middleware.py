import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.core.security import get_tenant_id_from_token

_NO_AUTH_PATHS = {"/", "/token", "/docs", "/redoc", "/openapi.json", "/metrics"}


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response


class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip tenant extraction for non-auth paths
        if request.url.path in _NO_AUTH_PATHS or request.url.path.startswith("/docs"):
            request.state.tenant_id = "default_tenant"
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        tenant_id = "default_tenant"

        if auth_header.startswith("Bearer "):
            token = auth_header[len("Bearer "):]
            extracted = get_tenant_id_from_token(token)
            if extracted:
                tenant_id = extracted

        request.state.tenant_id = tenant_id
        return await call_next(request)


def add_middleware(app):
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(TenantMiddleware)
