# EKA-AI v7.0 — Deployment Checklist

## Pre-Deployment Verification

### Local Development ✅
- [ ] Run `.\verify_system.ps1` — all checks pass
- [ ] Run `.\run_tests.ps1` — 100% tests pass
- [ ] Start server: `uvicorn app.main:app --reload`
- [ ] Visit http://localhost:8000/docs — all endpoints visible
- [ ] Login with admin/admin — JWT token obtained
- [ ] Test all endpoints via Swagger UI

### Code Quality ✅
- [ ] No syntax errors: `python -m py_compile app/**/*.py`
- [ ] Linting passes: `ruff check app/`
- [ ] Formatting passes: `black --check app/`
- [ ] Type hints present (optional)

### Documentation ✅
- [ ] README.md updated
- [ ] QUICKSTART.md reviewed
- [ ] ARCHITECTURE.md accurate
- [ ] API_DOCUMENTATION.md complete
- [ ] DEPLOYMENT_GUIDE.md ready

---

## Environment Setup

### Development Environment
- [ ] Python 3.9+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] .env file configured (copy from .env.example)
- [ ] GEMINI_API_KEY set
- [ ] Database initialized: `python init_db.py`

### Staging Environment
- [ ] PostgreSQL 14+ installed
- [ ] Redis 6+ installed
- [ ] DATABASE_URL configured (PostgreSQL)
- [ ] REDIS_URL configured
- [ ] SECRET_KEY generated: `openssl rand -hex 32`
- [ ] ALLOWED_ORIGINS set to staging frontend URL
- [ ] SENTRY_DSN configured (optional)
- [ ] SSL/TLS certificates installed

### Production Environment
- [ ] PostgreSQL cluster (HA)
- [ ] Redis cluster (HA)
- [ ] Load balancer configured
- [ ] Firewall rules set
- [ ] Monitoring configured (Prometheus + Grafana)
- [ ] Alerting configured (PagerDuty/Slack)
- [ ] Backup strategy implemented
- [ ] Disaster recovery plan documented

---

## Security Checklist

### Authentication & Authorization
- [ ] SECRET_KEY changed from default
- [ ] ACCESS_TOKEN_EXPIRE_MINUTES set appropriately (30 min recommended)
- [ ] Default admin password changed
- [ ] RBAC permissions reviewed
- [ ] JWT expiry tested

### Network Security
- [ ] HTTPS/TLS enabled
- [ ] CORS origins restricted (no wildcards in production)
- [ ] Rate limiting configured
- [ ] Firewall rules applied
- [ ] Database not publicly accessible

### Data Security
- [ ] Tenant isolation verified
- [ ] Audit logs enabled
- [ ] PII handling reviewed
- [ ] Backup encryption enabled
- [ ] Database credentials rotated

---

## Database Checklist

### SQLite (Development Only)
- [ ] Database file created: `eka_ai.db`
- [ ] Seed data loaded: `python init_db.py`
- [ ] Backup strategy: manual file copy

### PostgreSQL (Staging/Production)
- [ ] Database created: `CREATE DATABASE eka_ai;`
- [ ] User created with appropriate permissions
- [ ] pgvector extension installed: `CREATE EXTENSION vector;`
- [ ] Connection pooling configured
- [ ] Migrations run: `alembic upgrade head`
- [ ] Seed data loaded: `python init_db.py`
- [ ] Backup strategy: pg_dump + WAL archiving
- [ ] Replication configured (production)

---

## Redis Checklist

### Development (Optional)
- [ ] Redis running: `docker run -d -p 6379:6379 redis:alpine`
- [ ] REDIS_URL set in .env
- [ ] Connection tested: `redis-cli PING`

### Staging/Production
- [ ] Redis cluster deployed (3+ nodes)
- [ ] Persistence enabled (AOF + RDB)
- [ ] Maxmemory policy set: `allkeys-lru`
- [ ] Password authentication enabled
- [ ] TLS enabled (production)
- [ ] Monitoring configured
- [ ] Backup strategy implemented

---

## Monitoring & Observability

### Metrics
- [ ] Prometheus scraping /metrics endpoint
- [ ] Grafana dashboards configured
- [ ] Key metrics tracked:
  - [ ] Request rate (req/s)
  - [ ] Response time (p50, p95, p99)
  - [ ] Error rate (%)
  - [ ] Database connection pool usage
  - [ ] Redis cache hit rate
  - [ ] Active sessions

### Logging
- [ ] LOG_LEVEL set appropriately (INFO for production)
- [ ] JSON_LOGS enabled for production
- [ ] Log aggregation configured (ELK/Splunk)
- [ ] Log retention policy set
- [ ] Correlation IDs present in all logs

### Error Tracking
- [ ] Sentry DSN configured
- [ ] Error alerts configured
- [ ] Error rate threshold set
- [ ] On-call rotation defined

### Alerting
- [ ] High error rate alert (>5%)
- [ ] High response time alert (p95 >1s)
- [ ] Database connection pool exhaustion
- [ ] Redis unavailable
- [ ] Disk space low (<20%)
- [ ] Memory usage high (>80%)

---

## Performance Checklist

### Load Testing
- [ ] Load test plan created
- [ ] Target: 1000 req/s sustained
- [ ] Load test executed (Locust/k6)
- [ ] Results documented
- [ ] Bottlenecks identified and resolved

### Optimization
- [ ] Database indexes verified
- [ ] Redis caching enabled
- [ ] Connection pooling configured
- [ ] Async I/O verified
- [ ] Static assets cached (if applicable)

### Capacity Planning
- [ ] Expected user count documented
- [ ] Peak load estimated
- [ ] Infrastructure sized appropriately
- [ ] Auto-scaling configured (if cloud)

---

## Deployment Steps

### 1. Pre-Deployment
- [ ] Code freeze announced
- [ ] Deployment window scheduled
- [ ] Stakeholders notified
- [ ] Rollback plan documented
- [ ] Backup taken

### 2. Deployment
- [ ] Pull latest code: `git pull origin main`
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Run migrations: `alembic upgrade head`
- [ ] Restart application: `systemctl restart eka-ai`
- [ ] Verify startup: `curl http://localhost:8000/`

### 3. Post-Deployment
- [ ] Smoke tests pass: `./smoke_test.sh`
- [ ] Health check passes: `curl http://localhost:8000/`
- [ ] Metrics endpoint accessible: `curl http://localhost:8000/metrics`
- [ ] Login tested
- [ ] Key workflows tested:
  - [ ] Create vehicle
  - [ ] Create job card
  - [ ] Query chat
  - [ ] Calculate MG
  - [ ] View dashboard

### 4. Monitoring
- [ ] Monitor error rate (first 1 hour)
- [ ] Monitor response time (first 1 hour)
- [ ] Check logs for errors
- [ ] Verify Redis cache hit rate
- [ ] Verify database connection pool

### 5. Rollback (If Needed)
- [ ] Stop application
- [ ] Restore database backup
- [ ] Checkout previous version: `git checkout <previous-tag>`
- [ ] Restart application
- [ ] Verify rollback successful
- [ ] Notify stakeholders

---

## Testing Checklist

### Unit Tests
- [ ] All unit tests pass: `pytest tests/unit/`
- [ ] Coverage >90%: `pytest --cov=app tests/unit/`

### Integration Tests
- [ ] All integration tests pass: `pytest tests/integration/`
- [ ] Auth flow tested
- [ ] Job card workflow tested
- [ ] Chat with RAG tested
- [ ] Dashboard queries tested

### End-to-End Tests
- [ ] User registration/login
- [ ] Vehicle creation
- [ ] Job card creation → estimate → invoice
- [ ] Chat query with vehicle context
- [ ] MG calculation
- [ ] Dashboard viewing

### Performance Tests
- [ ] Load test: 1000 req/s sustained
- [ ] Stress test: find breaking point
- [ ] Soak test: 24 hours at 50% capacity
- [ ] Spike test: sudden 10x traffic

---

## Compliance Checklist

### Data Privacy
- [ ] GDPR compliance reviewed (if applicable)
- [ ] Data retention policy defined
- [ ] User data deletion process documented
- [ ] Privacy policy updated

### Security
- [ ] Penetration testing completed
- [ ] Vulnerability scan passed
- [ ] Security audit completed
- [ ] Incident response plan documented

### Audit
- [ ] Audit logs enabled
- [ ] Audit log retention policy set
- [ ] Audit log review process defined

---

## Documentation Checklist

### Technical Documentation
- [ ] Architecture diagram updated
- [ ] API documentation complete
- [ ] Database schema documented
- [ ] Deployment guide updated
- [ ] Runbook created

### User Documentation
- [ ] User guide created
- [ ] API examples provided
- [ ] FAQ updated
- [ ] Video tutorials (optional)

### Operations Documentation
- [ ] Monitoring guide
- [ ] Troubleshooting guide
- [ ] Backup/restore procedures
- [ ] Disaster recovery plan
- [ ] On-call runbook

---

## Sign-Off

### Development Team
- [ ] Code review completed
- [ ] Tests passing
- [ ] Documentation updated
- [ ] Signed off by: _________________ Date: _______

### QA Team
- [ ] Functional testing completed
- [ ] Performance testing completed
- [ ] Security testing completed
- [ ] Signed off by: _________________ Date: _______

### Operations Team
- [ ] Infrastructure ready
- [ ] Monitoring configured
- [ ] Backup strategy verified
- [ ] Signed off by: _________________ Date: _______

### Product Owner
- [ ] Requirements met
- [ ] Acceptance criteria satisfied
- [ ] Ready for production
- [ ] Signed off by: _________________ Date: _______

---

## Post-Launch Checklist

### Week 1
- [ ] Monitor error rates daily
- [ ] Review user feedback
- [ ] Address critical bugs
- [ ] Performance tuning

### Month 1
- [ ] Review metrics and KPIs
- [ ] Capacity planning review
- [ ] Security audit
- [ ] User training sessions

### Quarter 1
- [ ] Feature usage analysis
- [ ] Cost optimization
- [ ] Roadmap planning
- [ ] Team retrospective

---

**Deployment Date**: ______________
**Deployed By**: ______________
**Version**: 7.0.0
**Status**: ☐ Pending ☐ In Progress ☐ Complete
