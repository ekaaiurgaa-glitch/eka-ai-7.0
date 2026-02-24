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

## What's Been Implemented (Feb 2025)

### Core Platform
- ✅ Async FastAPI application with SQLAlchemy
- ✅ JWT-based authentication with RBAC (8 permissions)
- ✅ Multi-tenant architecture with isolation
- ✅ Rate limiting via slowapi + Redis
- ✅ Full observability stack (OpenTelemetry, Jaeger, Prometheus, Sentry)

### AI/ML Features
- ✅ Domain classifier with logistic regression
- ✅ Auto-training on startup (non-blocking via lifespan)
- ✅ Keyword fallback when API unavailable
- ✅ RAG with Gemini embeddings (`gemini-embedding-001`)

### Business Modules
- ✅ Chat module with governance gates
- ✅ Job Cards with FSM (OPEN → DIAGNOSIS → APPROVED → IN_PROGRESS → COMPLETED → CLOSED)
- ✅ MG Engine (deterministic cost calculations)
- ✅ Operator module with preview/confirm pattern
- ✅ Dashboard (workshop, fleet, owner views)
- ✅ Invoices, Vehicles, Catalog, Knowledge modules

### Testing
- ✅ 51 tests total (20 unit + 31 integration)
- ✅ 100% test pass rate
- ✅ pytest with pytest-asyncio

## Technical Stack
- **Backend:** FastAPI (async)
- **Database:** PostgreSQL with pgvector (prod), SQLite+aiosqlite (dev/test)
- **ORM:** Async SQLAlchemy
- **Auth:** JWT (python-jose)
- **AI/ML:** Google Gemini, Scikit-learn
- **Observability:** OpenTelemetry, Jaeger, Prometheus, Sentry
- **Testing:** pytest, pytest-asyncio, httpx

## Current Status: 8.9/10

### What Works
- All 51 tests passing
- Full async architecture
- JWT + RBAC authentication
- Domain gate ML classification
- Auto-training on startup
- Governance gates
- All business modules

### What's NOT Validated
- Load testing (10k req/s claim unverified)
- ML accuracy on held-out test set
- Multi-region deployment
- Chaos testing / failover

## P0 (Completed)
- [x] Fix async domain_gate call
- [x] Fix context_gate test expectations
- [x] Fix schema validation issues (tenant_id)
- [x] Fix datetime timezone comparisons
- [x] Update embedding model to gemini-embedding-001
- [x] Complete test suite (51/51 passing)

## P1 (Next)
- [ ] Load testing validation (1000+ req/s)
- [ ] ML accuracy on held-out dataset
- [ ] Multi-instance deployment behind load balancer
- [ ] Failover testing

## P2 (Future)
- [ ] Multi-region active-active deployment
- [ ] Chaos testing automation
- [ ] Production secrets management (Vault/AWS)
- [ ] Auto-scaling based on metrics

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
- (Configurable via .env)

## Notes
- Gemini API key quota may be exhausted - fallback to keyword matching works
- gRPC/Jaeger errors are expected when tracing backend not running
- Model retraining happens automatically on startup if model missing
