# EKA-AI Platform — Product Requirements Document

## Original Problem Statement
CTO-level analysis and iterative improvement of the EKA-AI.7.0 repository - a multi-tenant, asynchronous FastAPI application for automobile intelligence. The project required fixing identified issues and implementing an automated ML model training mechanism on application startup.

## Core Requirements
1. **Asynchronous Architecture** - Full async FastAPI with SQLAlchemy
2. **4-Stage Governance System** - Domain gate, Permission gate, Context gate, Confidence gate
3. **Deterministic Financial Engine (MG Engine)** - No AI math, pure calculations
4. **FSM for Job Cards** - State machine for workshop workflow
5. **RAG Implementation** - Using Gemini embeddings and pgvector
6. **Multi-tenant Architecture** - Tenant isolation via JWT claims
7. **Automated ML Training** - Non-blocking startup training via lifespan

## Current Status: 9.0/10

### Test Results
- **51/51 tests passing** (20 unit + 31 integration)
- All P1 features implemented
- All P2 features implemented

## What's Been Implemented (Feb 25, 2025)

### Bug Fixes (Session 2)
- ✅ Fixed async domain_gate call (missing await)
- ✅ Fixed schema validation (tenant_id optional, set from JWT)
- ✅ Fixed datetime timezone comparison in operator module
- ✅ Updated embedding model to gemini-embedding-001
- ✅ Fixed test file name collision
- ✅ Fixed estimate schema flexibility

### P1 Features (Completed)
- ✅ Load testing framework (`scripts/run_load_test.py`)
- ✅ ML accuracy validation with held-out test set (`scripts/validate_ml_accuracy.py`)
- ✅ Multi-instance deployment validator (`scripts/validate_multi_instance.py`)

### P2 Features (Completed)
- ✅ Chaos testing framework (`scripts/chaos_test.py`)
- ✅ Production secrets management (`app/core/secrets.py`)
- ✅ Multi-region deployment config (`docker/docker-compose.multi-region.yml`)
- ✅ Nginx load balancer config (`docker/nginx-lb.conf`)

### Core Platform (Previous Sessions)
- ✅ Async FastAPI application with SQLAlchemy
- ✅ JWT-based authentication with RBAC (8 permissions)
- ✅ Multi-tenant architecture with isolation
- ✅ Rate limiting via slowapi + Redis
- ✅ Full observability stack (OpenTelemetry, Jaeger, Prometheus, Sentry)

### AI/ML Features
- ✅ Domain classifier with logistic regression
- ✅ Auto-training on startup (non-blocking via lifespan)
- ✅ Keyword fallback when API unavailable (91.67% accuracy)
- ✅ RAG with Gemini embeddings

### Business Modules
- ✅ Chat module with governance gates
- ✅ Job Cards with FSM
- ✅ MG Engine (deterministic cost calculations)
- ✅ Operator module with preview/confirm pattern
- ✅ Dashboard (workshop, fleet, owner views)
- ✅ Invoices, Vehicles, Catalog, Knowledge modules

## Technical Stack
- **Backend:** FastAPI (async)
- **Database:** PostgreSQL with pgvector (prod), SQLite+aiosqlite (dev/test)
- **ORM:** Async SQLAlchemy
- **Auth:** JWT (python-jose)
- **AI/ML:** Google Gemini, Scikit-learn
- **Observability:** OpenTelemetry, Jaeger, Prometheus, Sentry
- **Testing:** pytest, pytest-asyncio, httpx
- **Load Testing:** Locust
- **Deployment:** Docker, nginx, multi-region support

## Key Files Reference

### Bug Fix Files
- `app/modules/chat/service.py` - async domain_gate fix
- `app/modules/chat/schema.py` - optional fields
- `app/modules/mg_engine/schema.py` - optional tenant_id
- `app/modules/mg_engine/router.py` - populate tenant_id
- `app/modules/job_cards/schema.py` - flexible estimates
- `app/modules/operator/tool_handler.py` - timezone fix
- `app/modules/knowledge/service.py` - embedding model update

### New Feature Files
- `scripts/run_load_test.py` - Load testing
- `scripts/validate_ml_accuracy.py` - ML validation
- `scripts/validate_multi_instance.py` - Multi-instance testing
- `scripts/chaos_test.py` - Chaos engineering
- `app/core/secrets.py` - Secrets management
- `docker/docker-compose.multi-region.yml` - Multi-region
- `docker/nginx-lb.conf` - Load balancer

## Remaining Work (Optional Enhancements)
- Production deployment validation
- Real load test with actual traffic
- Multi-region database replication setup

## Key API Endpoints
- `POST /token` - Authentication
- `POST /api/v1/chat/query` - Main AI chat
- `POST /api/v1/job-cards` - Create job
- `PATCH /api/v1/job-cards/{id}/transition` - FSM transition
- `POST /api/v1/mg/calculate` - MG calculation
- `POST /api/v1/operator/execute` - Preview action
- `POST /api/v1/operator/confirm` - Execute action
- `GET /health` - Health check

## Default Credentials
- Username: `admin`
- Password: `admin`

## Notes
- Gemini API key quota exhausted - fallback to keyword matching works (91.67% accuracy)
- gRPC/Jaeger errors are expected when tracing backend not running
- Model retraining happens automatically on startup if model missing

