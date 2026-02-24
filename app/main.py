from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.monitoring import MonitoringMiddleware, metrics_endpoint, setup_sentry
from app.core.logging_config import setup_logging
from app.core.middleware import TenantMiddleware, CorrelationIdMiddleware
from app.core.security import create_access_token
from app.core.dependencies import get_db
from app.modules.chat.router import router as chat_router
from app.modules.job_cards.router import router as job_cards_router
from app.modules.mg_engine.router import router as mg_engine_router
from app.modules.operator.router import router as operator_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.invoices.router import router as invoices_router
from app.modules.vehicles.router import router as vehicles_router
from app.modules.catalog.router import router as catalog_router
from app.modules.knowledge.router import router as knowledge_router

setup_logging(log_level=settings.LOG_LEVEL, json_logs=settings.JSON_LOGS)
setup_sentry(settings.SENTRY_DSN)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="7.0.0",
    description="EKA-AI — Governed Automobile Intelligence Platform",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Rate limiting (graceful no-op if Redis unavailable)
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    limiter = Limiter(
        key_func=get_remote_address,
        storage_uri=settings.REDIS_URL or "memory://",
        default_limits=[settings.RATE_LIMIT_DEFAULT],
    )
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    _rate_limiting_enabled = True
except Exception:
    _rate_limiting_enabled = False

# Middleware stack (applied in reverse order of declaration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(MonitoringMiddleware)
app.add_middleware(TenantMiddleware)
app.add_middleware(CorrelationIdMiddleware)


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to EKA-AI Platform v7.0", "status": "operational"}


@app.post("/token", tags=["Auth"])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Development login endpoint.
    Default credentials: admin / admin
    Returns a JWT with full permissions embedded.
    """
    if form_data.username != "admin" or form_data.password != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={
            "sub": form_data.username,
            "tenant_id": "tenant_admin",
            "permissions": [
                "chat_access",
                "can_create_invoice",
                "can_manage_jobs",
                "can_manage_estimates",
                "can_manage_vehicles",
                "can_execute_operator",
                "can_manage_catalog",
            ],
        }
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Route registrations
app.include_router(chat_router, prefix=settings.API_V1_STR, tags=["Chat"])
app.include_router(job_cards_router, prefix=settings.API_V1_STR, tags=["Job Cards"])
app.include_router(mg_engine_router, prefix=settings.API_V1_STR, tags=["MG Engine"])
app.include_router(operator_router, prefix=settings.API_V1_STR, tags=["Operator"])
app.include_router(dashboard_router, prefix=settings.API_V1_STR, tags=["Dashboard"])
app.include_router(invoices_router, prefix=settings.API_V1_STR, tags=["Invoices"])
app.include_router(vehicles_router, prefix=settings.API_V1_STR, tags=["Vehicles"])
app.include_router(catalog_router, prefix=settings.API_V1_STR, tags=["Catalog"])
app.include_router(knowledge_router, prefix=settings.API_V1_STR, tags=["Knowledge / RAG"])

app.add_route("/metrics", metrics_endpoint)
