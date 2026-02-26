# EKA-AI v7.0 → v8.0 Roadmap: 8.1 to 9/10

## Current Status: 8.1/10 ✅

### What Was Just Fixed (8.1 Blockers)

1. ✅ **Root main.py governance violation** — Moved to `experiments/gemini_prototype.py`
2. ✅ **Hardcoded admin credentials** — Now env-based (`ADMIN_USERNAME`, `ADMIN_PASSWORD`)
3. ⏳ **SQLite in production** — Documented, PostgreSQL migration guide ready

---

## Path to 9/10: Enterprise-Grade

### 🔴 Critical (Required for 9/10)

#### 1. PostgreSQL as Default Database
**Current**: SQLite with async support
**Target**: PostgreSQL + pgvector as default

**Changes**:
- Update `.env.example`: `DATABASE_URL=postgresql+asyncpg://user:password@localhost/eka_ai`
- Update `QUICKSTART.md`: PostgreSQL setup instructions first
- Add `docker-compose.yml` with PostgreSQL + pgvector
- Update migration: Add `CREATE EXTENSION IF NOT EXISTS vector` to init script

**Effort**: 2 hours
**Impact**: Production-grade persistence

---

#### 2. pgvector RAG Implementation
**Current**: JSON embeddings in SQLite (in-memory numpy similarity)
**Target**: Native pgvector with `<=>` operator

**Changes**:
```python
# app/modules/knowledge/model.py
from pgvector.sqlalchemy import Vector

class KnowledgeChunk(Base, TenantMixin, TimestampMixin):
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(768))  # Native pgvector
    source_url = Column(String, default="")
    chunk_index = Column(Integer, default=0)
```

```python
# app/modules/knowledge/service.py
async def similarity_search(db: AsyncSession, query: str, tenant_id: str, top_k: int = 3):
    query_embedding = await get_embedding(query)
    result = await db.execute(
        select(model.KnowledgeChunk)
        .filter(model.KnowledgeChunk.tenant_id == tenant_id)
        .order_by(model.KnowledgeChunk.embedding.cosine_distance(query_embedding))
        .limit(top_k)
    )
    return result.scalars().all()
```

**Effort**: 3 hours
**Impact**: Scales to 1M+ chunks, 10x faster similarity search

---

#### 3. ML-Based Domain Gate
**Current**: Keyword/regex matching
**Target**: Fine-tuned classifier (automobile vs non-automobile)

**Approach**:
- Use Gemini text-embedding-004 + logistic regression
- Train on 1000 automobile queries + 1000 non-automobile queries
- Cache model in Redis, reload on startup
- Fallback to keyword gate if model unavailable

**Changes**:
```python
# app/ai/domain_classifier.py
import numpy as np
from sklearn.linear_model import LogisticRegression
import pickle

class DomainClassifier:
    def __init__(self):
        self.model = self._load_model()
    
    def _load_model(self):
        try:
            with open("models/domain_classifier.pkl", "rb") as f:
                return pickle.load(f)
        except:
            return None  # Fallback to keyword gate
    
    async def is_automobile_query(self, query: str) -> bool:
        if not self.model:
            return self._keyword_fallback(query)
        
        embedding = await get_embedding(query)
        prediction = self.model.predict([embedding])[0]
        return prediction == 1
```

**Effort**: 8 hours (including training data collection)
**Impact**: 95%+ accuracy, handles edge cases

---

#### 4. Complete MG Business Logic
**Current**: `monthly_km` ignored in formula
**Target**: Full wear-tear calculation with usage-based adjustment

**Changes**:
```python
# app/modules/mg_engine/deterministic_engine.py
def calculate_mg(request: schema.MGCalculationRequest) -> schema.MGCalculationResponse:
    vehicle_key = f"{request.make}_{request.model}_{request.fuel_type.value}"
    wear_tear_costs = _get_wear_tear_costs(vehicle_key)
    
    # Base costs
    annual_parts = wear_tear_costs["annual_parts_cost"]
    annual_labor = wear_tear_costs["annual_labor_cost"]
    
    # Usage adjustment (NEW)
    usage_multiplier = request.monthly_km / 1000  # Base: 1000 km/month
    annual_parts *= usage_multiplier
    
    # City adjustment
    city_adj = _get_city_labor_index(request.city)
    
    # Risk adjustment
    risk_adj = RISK_MULTIPLIER.get(request.usage_type, 1.0)
    
    # Warranty adjustment
    warranty_adj = 0.5 if request.warranty_status == "under_warranty" else 0.0
    
    final_annual_cost = (annual_parts + (annual_labor * city_adj)) * risk_adj * (1 - warranty_adj)
    monthly_mg = final_annual_cost / 12
    
    return schema.MGCalculationResponse(...)
```

**Effort**: 2 hours
**Impact**: Accurate pricing for high-usage fleets

---

### 🟡 Important (Nice-to-Have for 9/10)

#### 5. Distributed Tracing
**Current**: Correlation IDs in logs
**Target**: OpenTelemetry + Jaeger

**Changes**:
```python
# app/core/tracing.py
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

def setup_tracing():
    if not settings.JAEGER_ENDPOINT:
        return
    
    trace.set_tracer_provider(TracerProvider())
    jaeger_exporter = JaegerExporter(
        agent_host_name=settings.JAEGER_HOST,
        agent_port=settings.JAEGER_PORT,
    )
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(jaeger_exporter)
    )

# app/main.py
from app.core.tracing import setup_tracing
setup_tracing()
```

**Effort**: 4 hours
**Impact**: Debug distributed systems, trace request flows

---

#### 6. Automated Failover
**Current**: Single instance
**Target**: Multi-instance with health checks + load balancer

**Approach**:
- Add `/health` endpoint with DB + Redis checks
- Configure load balancer (nginx/HAProxy) with health checks
- Deploy 3+ instances behind load balancer
- Implement graceful shutdown (drain connections)

**Changes**:
```python
# app/main.py
@app.get("/health", tags=["Health"])
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        redis_ok = get_redis_client() is not None
        return {
            "status": "healthy",
            "database": "ok",
            "redis": "ok" if redis_ok else "degraded",
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Unhealthy: {e}")
```

**Effort**: 6 hours (including infrastructure)
**Impact**: 99.9% uptime, zero-downtime deployments

---

## Implementation Priority

### Sprint 1 (Week 1): Core Infrastructure
1. PostgreSQL as default (2h)
2. pgvector RAG (3h)
3. Complete MG logic (2h)

**Deliverable**: 8.5/10

---

### Sprint 2 (Week 2): Intelligence Upgrade
4. ML domain gate (8h)
5. Distributed tracing (4h)

**Deliverable**: 8.8/10

---

### Sprint 3 (Week 3): High Availability
6. Automated failover (6h)
7. Load testing (4h)
8. Chaos testing (4h)

**Deliverable**: 9.0/10 ✅

---

## Verification Checklist

### 9/10 Criteria
- [ ] PostgreSQL + pgvector in production
- [ ] ML domain gate with 95%+ accuracy
- [ ] Complete MG formula with usage adjustment
- [ ] Distributed tracing operational
- [ ] Multi-instance deployment with failover
- [ ] Load test: 1000 req/s sustained
- [ ] Chaos test: survives instance failure

---

## 10/10 Path (Future)

### Additional Requirements
- Multi-region deployment (3 regions)
- Auto-scaling (CPU/memory triggers)
- Blue-green deployments
- Canary releases
- A/B testing framework
- Real-time anomaly detection
- Predictive maintenance ML models
- Mobile SDK
- GraphQL API
- WebSocket real-time updates

**Effort**: 3-6 months
**Team**: 3-5 engineers

---

## Cost Estimate

| Item | Cost (Monthly) |
|------|----------------|
| PostgreSQL (managed) | $50-200 |
| Redis (managed) | $30-100 |
| Load balancer | $20-50 |
| 3x app instances | $150-300 |
| Monitoring (Datadog/New Relic) | $100-500 |
| **Total** | **$350-1150/month** |

---

## Success Metrics

| Metric | 8.1/10 | 9.0/10 | 10.0/10 |
|--------|--------|--------|---------|
| Uptime | 99% | 99.9% | 99.99% |
| Response Time (p95) | <500ms | <200ms | <100ms |
| Throughput | 100 req/s | 1000 req/s | 10000 req/s |
| RAG Accuracy | 80% | 95% | 98% |
| Domain Gate Accuracy | 85% | 95% | 99% |
| Test Coverage | 100% | 100% | 100% |

---

**Current Status**: 8.1/10 ✅
**Next Milestone**: 9.0/10 (3 weeks)
**Final Goal**: 10.0/10 (6 months)
