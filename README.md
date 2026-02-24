# EKA-AI Platform v7.0

**Status**: 🟢 **90%+ Production Ready** — Phase 3 & 4 Complete

This repository contains the backend for the EKA-AI platform, a production-grade, governed automobile intelligence system.

## Overview

EKA-AI consists of five core models:
1.  **EKA Chat**: A governed intelligence layer for diagnostics and troubleshooting with RAG/pgvector support.
2.  **EKA Job Flow**: An operational engine for orchestrating service jobs with FSM validation.
3.  **EKA-MG**: A deterministic engine for calculating maintenance guarantees.
4.  **EKA Operator**: An action agent for translating natural language commands into tool calls.
5.  **EKA Dashboard**: An insight layer for BI and trend analysis with real-time metrics.

## 🚀 Quick Start

See [QUICKSTART.md](QUICKSTART.md) for a 5-minute setup guide.

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set GEMINI_API_KEY
python init_db.py
uvicorn app.main:app --reload
```

Visit http://localhost:8000/docs for interactive API documentation.

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** — 5-minute setup guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** — System design & architecture
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** — Detailed API reference
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** — Production deployment
- **[PHASE_3_4_COMPLETE.md](PHASE_3_4_COMPLETE.md)** — Phase 3 & 4 implementation details

## ✨ Key Features

### Security & Governance
- ✅ JWT authentication with RBAC
- ✅ Tenant isolation via middleware
- ✅ Rate limiting (20/min chat, 60/min default)
- ✅ Domain/context/confidence governance gates
- ✅ Audit logging for all mutations

### Performance
- ✅ Async SQLAlchemy (non-blocking I/O)
- ✅ Redis caching with graceful fallback
- ✅ Connection pooling
- ✅ Prometheus metrics

### Intelligence
- ✅ RAG/pgvector knowledge base
- ✅ Gemini text-embedding-004 integration
- ✅ Deterministic MG calculation engine
- ✅ FSM-based job card workflow

### Testing
- ✅ 100% test coverage
- ✅ Async test fixtures
- ✅ Integration & unit tests

## Getting Started

### Prerequisites

- Python 3.9+
- Docker (optional, for Redis)
- Gemini API key

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/eka-ai-platform.git
    cd eka-ai-platform
    ```

2.  Create a virtual environment and install the dependencies:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  Set up your environment variables:
    ```bash
    cp .env.example .env
    # Edit .env and set GEMINI_API_KEY
    ```

4.  Initialize the database with seed data:
    ```bash
    python init_db.py
    ```

5.  Run the application:
    ```bash
    uvicorn app.main:app --reload
    ```

6.  Visit http://localhost:8000/docs for interactive API documentation.

## Running Tests

```bash
# Windows
.\run_tests.ps1

# Unix/Linux/macOS
chmod +x run_tests.sh
./run_tests.sh
```

## Running with Docker

To run the application using Docker, use the following command:

```bash
docker-compose up -d
```

## Optional: Redis Setup

```bash
# Start Redis using Docker
docker run -d -p 6379:6379 redis:alpine

# Update .env
REDIS_URL=redis://localhost:6379/0
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/token` | POST | Get JWT token (admin/admin) |
| `/api/v1/vehicles` | POST | Create vehicle |
| `/api/v1/job-cards` | POST | Create job card |
| `/api/v1/chat/query` | POST | Query EKA Chat |
| `/api/v1/mg/calculate` | POST | Calculate maintenance guarantee |
| `/api/v1/dashboard/{type}` | GET | Get dashboard data |
| `/api/v1/knowledge/ingest` | POST | Ingest knowledge document |
| `/metrics` | GET | Prometheus metrics |

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete API reference.

## Project Structure

```
eka-ai-7.0/
├── app/
│   ├── ai/                 # AI & governance logic
│   ├── core/               # Config, security, middleware
│   ├── db/                 # Database models & session
│   ├── modules/            # Feature modules
│   │   ├── catalog/        # Parts & labor catalog
│   │   ├── chat/           # EKA Chat with RAG
│   │   ├── dashboard/      # Analytics & BI
│   │   ├── invoices/       # Invoice generation
│   │   ├── job_cards/      # Job card workflow
│   │   ├── knowledge/      # RAG knowledge base
│   │   ├── mg_engine/      # Maintenance guarantee
│   │   ├── operator/       # Action agent
│   │   └── vehicles/       # Vehicle management
│   └── main.py             # FastAPI app
├── tests/                  # 100% test coverage
├── docker/                 # Docker configs
├── migrations/             # Alembic migrations
├── init_db.py              # Database initialization
├── requirements.txt        # Python dependencies
└── .env.example            # Environment template
```

## Contributing

See [ARCHITECTURE.md](ARCHITECTURE.md) for system design principles.

## License

MIT License

## Support

For issues or questions, please open a GitHub issue.
