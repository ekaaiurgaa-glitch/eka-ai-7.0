# EKA-AI v7.0 - Automobile Intelligence Platform

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-00a393.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61dafb.svg)](https://react.dev/)
[![Tests](https://img.shields.io/badge/tests-50%2F50%20passing-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)]()

> **Governed Intelligence for Automobile Workshops**

EKA-AI is a comprehensive AI-powered platform designed specifically for automobile workshops. It combines natural language processing, job card management, invoice generation, and predictive maintenance calculations with strict governance controls.

---

## 🚀 Features

### Core Modules
- **🤖 EKA Intelligence** - Natural language diagnostic assistant with domain restrictions
- **📋 Job Card Management** - Complete workflow from diagnosis to closure
- **💰 Invoicing** - GST-compliant invoices with PDF generation
- **🛡️ MG Engine** - Predictive maintenance cost calculations
- **👤 Operator AI** - Natural language command interface with confirmation gates
- **✅ Approval Workflow** - Multi-level approval system with notifications

### AI Governance (Constitutional AI)
- ✅ Domain restriction (automobile-only queries)
- ✅ Confirmation required for all actions
- ✅ Safety filters for harmful content
- ✅ Audit logging for all operations
- ✅ No prompt injection vulnerabilities

### Subscription Tiers
| Plan | Tokens/Month | Actions/Day | Job Cards | Features |
|------|--------------|-------------|-----------|----------|
| Free | 10,000 | 5 | 20 | Basic AI, Job Cards |
| Starter | 100,000 | 50 | 200 | + Analytics, MG Engine |
| Professional | 500,000 | 200 | 1,000 | + Advanced AI, Priority Support |
| Enterprise | Unlimited | Unlimited | Unlimited | + Custom Models, SLA |

---

## 📦 Quick Start

### Prerequisites
- Python 3.13+
- Node.js 20+
- PostgreSQL 16 (production) / SQLite (development)
- Gemini API Key

### Installation

```bash
# Clone repository
git clone https://github.com/ekaaiurgaa-glitch/eka-ai-7.0.git
cd eka-ai-7.0

# Backend setup
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd frontend
npm install
npm run build
cd ..

# Database setup
alembic upgrade head

# Environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Running the Application

```bash
# Terminal 1 - Backend
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2 - Frontend (dev mode)
cd frontend
npm run dev

# Or serve built frontend
# Backend serves static files from frontend/dist
```

Access the application at `http://localhost:3000`

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Integration tests only
pytest tests/integration/ -v

# With coverage
pytest --cov=app tests/

# Frontend tests
cd frontend
npm test
```

---

## 📁 Project Structure

```
eka-ai-7.0/
├── app/                    # FastAPI backend
│   ├── ai/                # AI/ML services
│   ├── core/              # Core services (config, notifications)
│   ├── modules/           # Business modules
│   │   ├── job_cards/     # Job card workflow
│   │   ├── invoices/      # Invoice management
│   │   ├── mg_engine/     # MG calculations
│   │   └── operator/      # Operator AI
│   └── db/                # Database models
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # Reusable UI
│   │   ├── pages/         # Page components
│   │   └── context/       # React contexts
├── tests/                 # Test suite
├── migrations/            # Database migrations
└── docs/                  # Documentation
```

See [docs/REPO_STRUCTURE.md](docs/REPO_STRUCTURE.md) for complete structure.

---

## 🔧 Configuration

### Environment Variables

```env
# Required
DATABASE_URL=sqlite+aiosqlite:///eka_ai.db
SECRET_KEY=your-secret-key-here
GEMINI_API_KEY=your-gemini-api-key

# Optional (for notifications)
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
SENDGRID_API_KEY=your-sendgrid-key

# Optional (monitoring)
SENTRY_DSN=your-sentry-dsn
```

See [docs/DEPLOYMENT_CHECKLIST.md](docs/DEPLOYMENT_CHECKLIST.md) for full configuration.

---

## 🚀 Deployment

### Docker

```bash
docker-compose up -d
```

### Kubernetes

```bash
kubectl apply -f k8s/
```

See [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for detailed instructions.

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [API Documentation](docs/API_DOCUMENTATION.md) | Complete API reference |
| [Architecture](docs/ARCHITECTURE.md) | System architecture |
| [P0 Checklist](docs/P0_CHECKLIST.md) | Critical fixes checklist |
| [Production Readiness](docs/PRODUCTION_READINESS_REPORT_v7.0.md) | v7.0 status report |
| [Deployment Guide](docs/DEPLOYMENT_GUIDE.md) | Deployment instructions |

---

## 🛡️ Security & Governance

### Constitutional AI Principles
1. **Domain Restriction** - Only automobile-related queries
2. **Confirmation Gates** - All actions require explicit approval
3. **Safety Filters** - Block harmful/inappropriate content
4. **Audit Trail** - Complete logging of all operations
5. **Data Privacy** - GDPR-compliant data handling

### Security Features
- JWT authentication (RS256, 15-min expiry)
- Role-based access control (RBAC)
- Tenant isolation
- SQL injection protection
- XSS protection
- Rate limiting

---

## 📈 Performance

- **API Response Time**: < 100ms (p95)
- **Frontend Load Time**: < 3s
- **AI Response Time**: < 2s
- **Concurrent Users**: 1000+ (load tested)

---

## 🤝 Contributing

This is a proprietary project. For contributions, please contact the maintainers.

---

## 📄 License

Proprietary - All rights reserved.

---

## 🆘 Support

For support and inquiries:
- Email: support@eka-ai.in
- Documentation: See `/docs` folder
- Issues: GitHub Issues (private repo)

---

## 🏆 Project Status

| Phase | Status | Completion |
|-------|--------|------------|
| P0 - Critical Fixes | ✅ Complete | 100% |
| P1 - High Priority | ✅ Complete | 100% |
| P2 - Medium Priority | ✅ Complete | 100% |
| **Overall** | **🚀 Production Ready** | **100%** |

See [docs/PRODUCTION_READINESS_REPORT_v7.0.md](docs/PRODUCTION_READINESS_REPORT_v7.0.md) for detailed status.

---

<p align="center">
  <strong>Built with ❤️ for Automobile Workshops</strong><br>
  <sub>© 2026 EKA-AI. All rights reserved.</sub>
</p>
