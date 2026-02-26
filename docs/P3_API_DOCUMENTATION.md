# P3 Enterprise Features - API Documentation

## MG Financial Risk & Reserve

### Calculate Reserve
```http
POST /api/v1/mg/financial/reserve/calculate
{
  "contract_value": 100000,
  "risk_level": "medium"
}
```

### Analyze Risk
```http
POST /api/v1/mg/financial/risk/analyze
{
  "contract_id": 1,
  "utilized": 50000,
  "reserve": 15000
}
```

## Unit Economics

### Get Unit Economics
```http
GET /api/v1/analytics/unit-economics?start_date=2026-01-01&end_date=2026-03-01
```

### Token Projections
```http
GET /api/v1/analytics/token-projections?months=6
```

## Data Privacy & Compliance

### Export User Data
```http
POST /api/v1/data-privacy/export
{
  "user_id": "user123"
}
```

### Delete User Data
```http
POST /api/v1/data-privacy/delete
{
  "user_id": "user123",
  "reason": "User request"
}
```

### Anonymize Data
```http
POST /api/v1/data-privacy/anonymize
{
  "user_id": "user123"
}
```

## Disaster Recovery

### DR Status
```http
GET /api/v1/dr/status
```

### Create Backup
```http
POST /api/v1/dr/backup
```

### Restore Backup
```http
POST /api/v1/dr/restore?backup_id=backup_123&region=us-east-1
```

### Failover
```http
POST /api/v1/dr/failover?region=eu-west-1
```

## Payments

### Create Payment
```http
POST /api/v1/payments/create
{
  "amount": 5000,
  "currency": "INR",
  "customer_email": "customer@example.com",
  "description": "Job card payment"
}
```

### Verify Payment
```http
GET /api/v1/payments/verify/{payment_id}
```

## Notifications

### Send SMS
```http
POST /api/v1/notifications/sms
{
  "to": "+919876543210",
  "message": "Your job card is ready"
}
```

### Send Email
```http
POST /api/v1/notifications/email
{
  "to": "customer@example.com",
  "subject": "Job Update",
  "body": "Your vehicle is ready"
}
```

### Send Approval Link
```http
POST /api/v1/notifications/approval-link?customer_email=test@example.com&job_no=JB-001&estimate_id=1
```

## Insurance

### Get Quote
```http
GET /api/v1/insurance/quote?vehicle_id=1&coverage=50000
```

### Bind Policy
```http
POST /api/v1/insurance/bind?quote_id=quote_123
```

## Contract Termination

### Calculate Refund
```http
POST /api/v1/mg/contracts/calculate-refund
{
  "contract_value": 100000,
  "start_date": "2026-01-01T00:00:00",
  "end_date": "2026-06-01T00:00:00"
}
```

### Terminate Contract
```http
POST /api/v1/mg/contracts/1/terminate?reason=Customer request
```

## Claims Reconciliation

### Monthly Report
```http
GET /api/v1/mg/claims/report/2026-02
```

### Reconcile Claims
```http
POST /api/v1/mg/claims/1/reconcile
```

## Additional Features

### LLM Fallback Chain
Automatic failover: Gemini → GPT-4 → Claude
Configured in `app/ai/llm_fallback.py`

### Degraded Mode
Keyword-based fallback when LLM unavailable
Configured in `app/ai/degraded_mode.py`

### Multi-language Support
```python
from app.i18n.translations import translate
message = translate("welcome", lang="hi")
```

### DDoS Protection
Automatic IP blocking after 100 requests/minute
Configured in `app/security/ddos_protection.py`

### Anti-abuse Detection
Token farming and rapid-fire detection
Configured in `app/security/anti_abuse.py`

### File Storage
S3/GCP abstraction for PDI images
Configured in `app/core/file_storage.py`

### Message Queue
Async job processing
Configured in `app/core/message_queue.py`

### Kubernetes Autoscaling
HPA manifest in `k8s/deployment.yaml`
Min: 3 replicas, Max: 20 replicas
CPU target: 70%
