from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from jose import jwt
import uuid
import logging
import json
from app.db.session import AsyncSessionLocal
from app.db.models import AuditLog
from app.core.config import settings

logger = logging.getLogger(__name__)

class TenantMiddleware(BaseHTTPMiddleware):
    """
    Extracts tenant_id from JWT and attaches to request state.
    """
    async def dispatch(self, request, call_next):
        # Skip for health checks and auth endpoints
        if request.url.path in ["/health", "/metrics"] or "/auth/" in request.url.path:
            return await call_next(request)
        
        # Public approval links might also skip this if they use a token instead
        if request.url.path.startswith("/api/v1/approvals/"):
             return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            # Fallback for dev/unauthenticated (should be blocked by RBAC dependencies later)
            request.state.tenant_id = "tenant_default"
            request.state.user_role = "customer"
            return await call_next(request)

        token = auth_header.split(" ")[1]
        try:
            # For now, we decode without verification to support the current testing setup
            payload = jwt.decode(token, "", options={"verify_signature": False})
            
            tenant_id = payload.get("tenant_id")
            if not tenant_id:
                tenant_id = payload.get("sub", "tenant_default")
            
            request.state.tenant_id = tenant_id
            request.state.user_role = payload.get("role", "customer")
            request.state.user_id = payload.get("user_id")
            request.state.user_permissions = payload.get("permissions", [])
        except Exception as e:
            logger.error(f"Middleware JWT decode failed: {e}")
            request.state.tenant_id = "tenant_default"
            request.state.user_role = "customer"

        return await call_next(request)

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Adds X-Correlation-ID to request/response for tracing.
    """
    async def dispatch(self, request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response

class AuditMiddleware(BaseHTTPMiddleware):
    """
    P1-22: Captures mutations (POST, PUT, PATCH, DELETE) and logs to AuditLog table.
    """
    async def dispatch(self, request, call_next):
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return await call_next(request)

        # Clone request body logic if needed, but for now we log basics
        response = await call_next(request)
        
        # Only log successful or client-error mutations (2xx, 4xx)
        if 200 <= response.status_code < 500:
            try:
                tenant_id = getattr(request.state, "tenant_id", "system")
                user_id = getattr(request.state, "user_id", "anonymous")
                
                async with AsyncSessionLocal() as db:
                    log = AuditLog(
                        entity_type="request",
                        entity_id=request.url.path,
                        actor_id=user_id,
                        action=request.method,
                        payload={
                            "path": request.url.path,
                            "query": str(request.query_params),
                            "status": response.status_code
                        },
                        tenant_id=tenant_id
                    )
                    db.add(log)
                    await db.commit()
            except Exception as e:
                logger.error(f"Audit middleware failed: {e}")

        return response
