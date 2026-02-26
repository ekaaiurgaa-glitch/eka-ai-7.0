# EKA-AI Deployment Guide

## GitHub Secrets Setup

Go to **Settings → Secrets and variables → Actions** and add:

- `GEMINI_API_KEY` - Your Google Gemini API key
- `STAGING_DATABASE_URL` - Staging PostgreSQL URL
- `PRODUCTION_DATABASE_URL` - Production PostgreSQL URL
- `SENTRY_DSN` - Sentry error tracking DSN (optional)

## Environment Configuration

Go to **Settings → Environments** and create:

**staging**
- No protection rules
- URL: https://staging.eka-ai.example.com

**production**
- Required reviewers
- Deployment branches: Only tags matching v*
- URL: https://eka-ai.example.com

## Monitoring Setup

### Prometheus + Grafana

```bash
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.monitoring.yml up -d
```

Access:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

### Sentry

```bash
pip install sentry-sdk[fastapi]
```

Add to .env:
```
SENTRY_DSN=https://your-dsn@sentry.io/project-id
```

## WebSocket Real-Time Updates

Connect:
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/tenant_123?token=your_token');
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

## Deployment Checklist

- [ ] Set GitHub secrets
- [ ] Configure environments
- [ ] Test Docker build
- [ ] Verify health endpoint
- [ ] Monitor metrics at /metrics
