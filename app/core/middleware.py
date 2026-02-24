import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response

# Placeholder for tenant middleware
# In a real application, this middleware would extract the tenant_id from the request
# (e.g., from a JWT or a header) and set it in a context variable for the rest of the application to use.
class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # tenant_id = extract_tenant_id_from_request(request)
        # set_tenant_in_context(tenant_id)
        response = await call_next(request)
        return response

def add_middleware(app):
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(TenantMiddleware)

