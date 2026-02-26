# Test Execution Guide

## Quick Start

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov httpx

# Run all tests
pytest -v

# Run with coverage
pytest -v --cov=app --cov-report=term-missing --cov-report=html

# Run specific test file
pytest tests/unit/test_governance.py -v

# Run specific test
pytest tests/integration/test_auth.py::test_login_success -v
```

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures (DB, client, auth)
├── unit/
│   ├── test_governance.py   # Domain/context/confidence gates
│   ├── test_catalog_service.py
│   ├── test_vehicle_service.py
│   ├── test_job_flow_fsm.py
│   └── test_mg_engine.py
└── integration/
    ├── test_auth.py         # Login, tokens, RBAC
    ├── test_job_cards.py    # Full job card lifecycle
    ├── test_invoices.py
    ├── test_mg_engine.py
    ├── test_operator.py     # Preview/confirm flow
    ├── test_dashboard.py
    └── test_chat.py         # Governance + RAG
```

## Coverage Target

- **Unit Tests:** 100% of business logic
- **Integration Tests:** All API endpoints
- **Overall Target:** 95%+

## Running Tests in CI/CD

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest -v --cov=app --cov-report=xml
      - uses: codecov/codecov-action@v3
```

## Test Database

Tests use in-memory SQLite:
- Fast execution
- No external dependencies
- Clean state per test
- Async-compatible

## Mocking External Services

Gemini API calls in tests:
- Use real API if GEMINI_API_KEY set
- Gracefully handle failures
- Mock responses for deterministic tests

Redis in tests:
- Uses memory:// backend
- No external Redis required
- Graceful fallback tested

## Debugging Failed Tests

```bash
# Run with verbose output
pytest -vv -s

# Run single test with print statements
pytest tests/unit/test_governance.py::test_domain_gate_allows_automobile_queries -vv -s

# Drop into debugger on failure
pytest --pdb

# Show local variables on failure
pytest -l
```

## Performance Testing

```bash
# Install locust
pip install locust

# Run load test
locust -f tests/load/locustfile.py --host=http://localhost:8080
```
