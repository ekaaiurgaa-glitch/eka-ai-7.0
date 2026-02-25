from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.subscriptions.enforcement import SubscriptionEnforcer
from app.core.dependencies import get_db
from app.core.cache import get_redis
import jwt


class SubscriptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip non-API routes
        if not request.url.path.startswith("/api/v1/"):
            return await call_next(request)
        
        # Skip auth endpoints
        if request.url.path in ["/api/v1/token", "/api/v1/health"]:
            return await call_next(request)
        
        # Extract tenant_id from JWT
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return await call_next(request)
        
        try:
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, options={"verify_signature": False})
            tenant_id = payload.get("tenant_id")
            
            if not tenant_id:
                return await call_next(request)
            
            # Determine action type from route
            action_type = self._get_action_type(request.url.path, request.method)
            
            # Check subscription
            db = next(get_db())
            redis = get_redis()
            enforcer = SubscriptionEnforcer(db, redis)
            
            result = await enforcer.check(tenant_id, action_type, tokens_estimate=0)
            
            if not result.allowed:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": {
                            "code": result.error_code,
                            "message": result.warning or "Subscription limit exceeded",
                            "retry_after": result.retry_after_seconds
                        }
                    }
                )
            
            # Add subscription headers
            response = await call_next(request)
            if result.warning:
                response.headers["X-Subscription-Warning"] = result.warning
            
            return response
            
        except Exception as e:
            # Don't block on enforcement errors
            return await call_next(request)
    
    def _get_action_type(self, path: str, method: str) -> str:
        """Map route to action type"""
        if "/chat/" in path:
            return "chat_query"
        elif "/operator/" in path:
            return "operator_action"
        elif "/job-cards" in path or "/job_cards" in path:
            if method == "POST":
                return "job_card_create"
        elif "/mg/" in path:
            return "mg_calculation"
        elif "/dashboard" in path:
            return "dashboard_load"
        elif "/data-export" in path:
            return "data_export"
        return "api_request"
