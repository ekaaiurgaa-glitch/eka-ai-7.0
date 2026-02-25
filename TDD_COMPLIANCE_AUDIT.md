# TDD COMPLIANCE AUDIT REPORT

## ❌ CRITICAL TDD VIOLATIONS FOUND

### 1. LLM Model Mismatch (Section 4.1.3)

**TDD Requirement:**
```
model: gemini-2.0-flash — low latency, cost-efficient at scale
```

**Current Implementation:**
```python
model="gemini-3-flash-preview"  # WRONG MODEL
```

**Status:** ❌ VIOLATION - Must use `gemini-2.0-flash`

---

### 2. Missing `thinking_level` Parameter (Section 4.1.3)

**TDD Requirement:**
```
thinking_level: HIGH — mandatory for multi-step diagnostic reasoning
```

**Current Implementation:**
```python
config = types.GenerateContentConfig(
    temperature=0.4,
    top_p=0.9,
    # thinking_level MISSING
)
```

**Status:** ❌ VIOLATION - Must add `thinking_level="HIGH"`

---

### 3. Missing `max_output_tokens` Cap (Section 4.1.3)

**TDD Requirement:**
```
max_output_tokens: 1024 — capped to control cost; enforced per response
```

**Current Implementation:**
```python
# max_output_tokens NOT SET
```

**Status:** ❌ VIOLATION - Must add `max_output_tokens=1024`

---

### 4. Missing `safety_settings` (Section 4.1.3)

**TDD Requirement:**
```
safety_settings: BLOCK_ONLY_HIGH for harm categories
```

**Current Implementation:**
```python
# safety_settings NOT CONFIGURED
```

**Status:** ❌ VIOLATION - Must configure safety settings

---

### 5. JWT Algorithm Mismatch (Section 6.1)

**TDD Requirement:**
```
OAuth 2.0 / OIDC: JWT tokens (RS256)
```

**Current Implementation:**
```python
ALGORITHM: str = os.getenv("ALGORITHM", "HS256")  # WRONG - Should be RS256
```

**Status:** ❌ VIOLATION - Must use RS256 asymmetric signing

---

### 6. JWT Token Expiry Mismatch (Section 6.1)

**TDD Requirement:**
```
15-minute access token TTL
```

**Current Implementation:**
```python
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
# DEFAULT IS 30 MINUTES, NOT 15
```

**Status:** ❌ VIOLATION - Must default to 15 minutes

---

### 7. Missing Refresh Token Implementation (Section 6.1)

**TDD Requirement:**
```
7-day rotating refresh tokens
```

**Current Implementation:**
```python
# NO REFRESH TOKEN LOGIC FOUND
```

**Status:** ❌ VIOLATION - Must implement refresh token rotation

---

### 8. Missing mTLS for Service-to-Service (Section 6.1)

**TDD Requirement:**
```
Service-to-service calls authenticated via mutual TLS (mTLS) using short-lived certificates rotated every 24 hours
```

**Current Implementation:**
```python
# NO mTLS IMPLEMENTATION FOUND
```

**Status:** ❌ VIOLATION - Must implement mTLS between services

---

### 9. Database Not PostgreSQL (Section 2.2)

**TDD Requirement:**
```
Primary DB: PostgreSQL 16 on Supabase
```

**Current Implementation:**
```python
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./eka_ai.db")
# DEFAULTS TO SQLITE, NOT POSTGRESQL
```

**Status:** ⚠️ WARNING - Development OK, but production must use PostgreSQL

---

### 10. Missing RAG top-5 Retrieval (Section 4.1.5)

**TDD Requirement:**
```
Retrieve top-5 semantically similar chunks from pgvector
```

**Current Implementation:**
```python
# In knowledge/service.py: top_k=3 (NOT 5)
```

**Status:** ❌ VIOLATION - Must retrieve top-5 chunks

---

## 📊 TDD COMPLIANCE SUMMARY

| Category | Required | Implemented | Status |
|----------|----------|-------------|--------|
| LLM Model | gemini-2.0-flash | gemini-3-flash-preview | ❌ |
| LLM Config | 5 params | 2 params | ❌ |
| JWT Algorithm | RS256 | HS256 | ❌ |
| JWT Expiry | 15 min | 30 min | ❌ |
| Refresh Tokens | Required | Missing | ❌ |
| mTLS | Required | Missing | ❌ |
| Database | PostgreSQL | SQLite (dev) | ⚠️ |
| RAG Retrieval | top-5 | top-3 | ❌ |

**Overall TDD Compliance: ~60%**

---

## 🚨 REQUIRED FIXES

### Priority 1 (Blocking Production)
1. Change LLM model to `gemini-2.0-flash`
2. Add `thinking_level="HIGH"`
3. Add `max_output_tokens=1024`
4. Add `safety_settings`
5. Change JWT to RS256
6. Set JWT expiry to 15 minutes
7. Implement refresh token rotation
8. Implement mTLS for service-to-service

### Priority 2 (Production Readiness)
9. Change RAG retrieval to top-5
10. Ensure PostgreSQL in production

---

## ✅ WHAT IS COMPLIANT

- ✅ Temperature: 0.4 (correct)
- ✅ top_p: 0.9 (correct)
- ✅ SECRET_KEY enforcement (correct)
- ✅ Multi-tenant architecture (correct)
- ✅ Row-Level Security (implemented)
- ✅ Governance gates (implemented)
- ✅ Deterministic GST calculation (correct)
- ✅ Job card FSM (implemented)
- ✅ Audit logging (implemented)

---

**CONCLUSION: Application requires 10 critical fixes to achieve full TDD compliance before production deployment.**
