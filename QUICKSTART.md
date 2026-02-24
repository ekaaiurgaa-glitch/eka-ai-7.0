# EKA-AI v7.0 — Quick Start Guide

## 🚀 5-Minute Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and set GEMINI_API_KEY
```

### 3. Initialize Database

```bash
python init_db.py
```

### 4. Start Server

```bash
uvicorn app.main:app --reload
```

### 5. Get JWT Token

```bash
curl -X POST http://localhost:8000/token \
  -d "username=admin&password=admin"
```

Copy the `access_token` from the response.

### 6. Test API

Visit http://localhost:8000/docs and click "Authorize" to paste your token.

---

## 📋 Common Tasks

### Create a Vehicle

```bash
curl -X POST http://localhost:8000/api/v1/vehicles \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "plate_number": "MH12AB1234",
    "make": "Maruti",
    "model": "Swift",
    "year": 2019,
    "fuel_type": "petrol",
    "owner_name": "John Doe"
  }'
```

### Create a Job Card

```bash
curl -X POST http://localhost:8000/api/v1/job-cards \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": 1,
    "complaint": "Brake noise when stopping"
  }'
```

### Query EKA Chat

```bash
curl -X POST http://localhost:8000/api/v1/chat/query \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Why is my car making a grinding noise when I brake?",
    "vehicle": {
      "make": "Maruti",
      "model": "Swift",
      "year": 2019,
      "fuel": "petrol"
    }
  }'
```

### Calculate Maintenance Guarantee

```bash
curl -X POST http://localhost:8000/api/v1/mg/calculate \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "make": "Tata",
    "model": "Nexon",
    "fuel_type": "diesel",
    "city": "Mumbai",
    "usage_type": "personal",
    "warranty_status": "expired"
  }'
```

### Ingest Knowledge Document

```bash
curl -X POST http://localhost:8000/api/v1/knowledge/ingest \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Brake Maintenance Guide",
    "content": "Regular brake inspection is crucial. Grinding noise indicates worn pads.",
    "source_url": "https://example.com/brake-guide"
  }'
```

---

## 🧪 Running Tests

```bash
# Windows
.\run_tests.ps1

# Unix/Linux/macOS
chmod +x run_tests.sh
./run_tests.sh
```

---

## 🔧 Optional: Redis Setup

### Using Docker

```bash
docker run -d -p 6379:6379 redis:alpine
```

### Update .env

```env
REDIS_URL=redis://localhost:6379/0
```

### Verify Caching

```bash
# Start Redis CLI
redis-cli

# Monitor cache operations
MONITOR
```

---

## 📊 Monitoring

### Prometheus Metrics

Visit http://localhost:8000/metrics

### Health Check

```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "message": "Welcome to EKA-AI Platform v7.0",
  "status": "operational"
}
```

---

## 🐛 Troubleshooting

### Database Locked Error (SQLite)

**Solution**: Use PostgreSQL for production or ensure only one process accesses SQLite.

### Redis Connection Failed

**Solution**: Redis is optional. The app will run with in-memory fallback. Check logs for warnings.

### Rate Limit Exceeded (429)

**Solution**: Wait 1 minute or increase `RATE_LIMIT_CHAT` / `RATE_LIMIT_DEFAULT` in .env.

### Gemini API Error

**Solution**: Verify `GEMINI_API_KEY` is set correctly in .env. Check API quota.

### Import Errors

**Solution**: Reinstall dependencies:
```bash
pip install -r requirements.txt --force-reinstall
```

---

## 📚 Key Endpoints

| Endpoint | Method | Description | Permission |
|----------|--------|-------------|------------|
| `/token` | POST | Get JWT token | Public |
| `/api/v1/vehicles` | POST | Create vehicle | `can_manage_vehicles` |
| `/api/v1/job-cards` | POST | Create job card | `can_manage_jobs` |
| `/api/v1/job-cards/{id}/estimate` | POST | Create estimate | `can_manage_estimates` |
| `/api/v1/invoices` | POST | Create invoice | `can_create_invoice` |
| `/api/v1/chat/query` | POST | Query EKA Chat | `chat_access` |
| `/api/v1/mg/calculate` | POST | Calculate MG | Authenticated |
| `/api/v1/operator/execute` | POST | Execute operator | `can_execute_operator` |
| `/api/v1/dashboard/{type}` | GET | Get dashboard | Authenticated |
| `/api/v1/knowledge/ingest` | POST | Ingest knowledge | `can_manage_catalog` |
| `/api/v1/catalog/parts` | GET | List parts | `can_manage_estimates` |

---

## 🔐 Default Credentials

**Username**: `admin`
**Password**: `admin`

**Permissions**: All (full access)

⚠️ **Change these in production!**

---

## 📖 Further Reading

- [ARCHITECTURE.md](ARCHITECTURE.md) — System design & architecture
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) — Detailed API reference
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) — Production deployment
- [PHASE_3_4_COMPLETE.md](PHASE_3_4_COMPLETE.md) — Implementation details

---

## 💡 Tips

1. **Use /docs**: FastAPI auto-generates interactive API docs at http://localhost:8000/docs
2. **Check logs**: Structured logs show all operations with correlation IDs
3. **Monitor metrics**: Prometheus metrics at /metrics track performance
4. **Test first**: Run tests before making changes: `.\run_tests.ps1`
5. **Redis optional**: App works without Redis, but caching improves performance

---

**Need help?** Check the logs or open an issue on GitHub.
