# EKA-AI — Detailed model-by-model architecture, working flows, repo layout and pricing linkage

*(Production-grade specification: implementation-ready, copy-paste friendly for VS Code / Antigravity)*

---

This document explains each of the **five core EKA models** separately (purpose, inputs/outputs, APIs, data models, governance checks, error handling, test strategy), shows how they integrate in end-to-end flows, and describes exactly **how pricing and subscriptions** are linked to system behavior. At the end you’ll find a production-ready **GitHub repo structure** and concrete implementation guidance (DB design patterns, function signatures, example JSONs, CI/CD & observability pointers).

&gt; Note: every model strictly follows the EKA Constitution: Domain Gate, Permission Gate, Context Gate, Confidence Gate. All financial math (GST, MG) is deterministic code — **never** produced by the LLM.

---

# 1 — EKA Chat (Governed Intelligence Layer)

### Purpose

* Provide structured, domain-locked automobile intelligence: diagnostics, troubleshooting, service procedure guidance, parts explanation.
* Advisory only — **no DB writes**, **no pricing**, **no state transitions**.

### Core responsibilities

* Validate request via Governance Gates.
* Perform RAG against knowledge DB (pgvector) when required.
* Return structured responses in mandated format:

  ```
  Issue Summary:
  Probable Causes:
  - ...
  Diagnostic Steps:
  1. ...
  Safety Advisory:
  Confidence Level: &lt;numeric %&gt;
  ```

### Inputs

* Natural language query + optional structured vehicle context:

  ```json
  {
    "query": "brake grinding when stopping",
    "vehicle": {"make":"Maruti","model":"Swift","year":2019,"fuel":"petrol"},
    "tenant_id": "uuid-..."
  }
  ```

### Outputs

* Structured diagnostic object (JSON) + confidence score.
* Optional RAG references (doc ids) for traceability.

### Governance checks (pseudocode)

```py
if not is_automobile_query(query): return DOMAIN_GATE_DENY
if not has_permission(user, 'chat_access'): return PERMISSION_DENY
if needs_diagnostic and not vehicle_context_complete(): return CONTEXT_REQUEST
result = llm_reason(...)
if result.confidence &lt; 90: return REQUEST_CLARIFICATION
return structured_response(result)
```

### API endpoints

* `POST /api/v1/chat/query` — validates gates, calls Gemini client with system_prompt, returns structured response.
* `GET /api/v1/chat/examples` — canned diagnostics templates.

### Data model (SQLAlchemy sketch)

* `chat_requests` (id, tenant_id, user_id, query_hash, vehicle_json, response_json, confidence, rag_refs, created_at)

### Tests

* Unit tests for gate logic.
* Integration tests that mock Gemini and vector DB to verify structured output format, confidence gating.

---

# 2 — EKA Job Flow (Operational Engine)

### Purpose

* Full workflow orchestrator for service jobs: Job Card lifecycle and deterministic rules enforcement.

### Lifecycle states

`OPEN → DIAGNOSIS → ESTIMATE → APPROVAL_PENDING → APPROVED → REPAIR → QC_PDI → READY → INVOICED → PAID → CLOSED`

### Core responsibilities

* Maintain immutable audit trail of state transitions.
* Enforce deterministic rules: no repair without approved estimate, no invoice without approval, mandatory PDI.
* Provide APIs used by UI and EKA Operator to advance flows.

### Key APIs (examples)

* `POST /api/v1/job_cards` — create job card (validated by Operator or manual).
* `GET /api/v1/job_cards/{id}`
* `PATCH /api/v1/job_cards/{id}/transition` — change state (checks rules).
* `POST /api/v1/job_cards/{id}/estimate` — create estimate; uses pricing catalog.
* `POST /api/v1/job_cards/{id}/approve` — mark approved (customer/owner).

### Pricing linkage in the flow

* The estimate stage pulls part prices from `catalog.parts` and labor from `catalog.labor_rates`.
* Each line item includes `hsn_code`, `tax_rate` (computed deterministically).
* Estimate → invoice transforms estimate lines to invoice lines (no LLM math).

### Data models (selected)

* `job_cards` (id, tenant_id, job_no, vehicle_id, complaint, state, created_by, created_at)
* `estimates` (id, job_id, lines jsonb, total_parts, total_labor, tax_breakdown, created_at)
* `audit_logs` (id, entity_type, entity_id, actor_id, action, payload, created_at)

### State transition enforcement (pseudocode)

```py
def transition_job(job, new_state, actor):
    if not allowed_transition(job.state, new_state): raise InvalidTransition
    if new_state == 'REPAIR' and not job.estimate.approved: raise RequireApproval
    job.state = new_state
    audit.log(...)
    save(job)
```

### Developer hooks

* Webhook events for `JOB_CARD_CREATED`, `ESTIMATE_APPROVED`, `INVOICE_GENERATED` to notify UI / payment gateway.

### Tests

* FSM unit tests: try illegal transitions and expect failure.
* Integration: full create → estimate → approve → invoice flow.

---

# 3 — EKA-MG (Maintenance Guarantee / Deterministic Engine)

### Purpose

* Deterministic engine that computes Annual Maintenance and Monthly MG subscription amounts using fixed formulas and curated matrices.

### Inputs (mandatory)

* `make, model, variant, fuel_type, year, city, monthly_km, warranty_status (under/out), usage_type (personal/commercial), tenant_id`

### Calculation layers

1. **Wear & Tear Matrix** — lookup replacement intervals & parts cost per model/variant.
2. **City Labor Index** — multiplier (city_code → multiplier table).
3. **Risk Multiplier** — based on `usage_type`, monthly_km bands, vehicle age.
4. **Warranty Adjustment** — exclude/discount warranty covered components.
5. **Annual → Monthly** — sum(costs) / 12 → MG.

### Output

```json
{
  "vehicle_profile": {...},
  "annual_parts": 48000,
  "annual_labor": 24000,
  "city_adj": 1.15,
  "risk_adj": 1.10,
  "warranty_adj": 0.0,
  "final_annual_cost": 92400,
  "monthly_mg": 7700,
  "breakdown": {"parts": ..., "labor": ...},
  "notes": "Final MG calculation must be executed by deterministic engine (backend)."
}
```

### Strict rules

* **LLM cannot compute MG**. LLM may only validate input completeness and show breakdown format.
* All numerical math done in `mg_engine/deterministic_engine.py`.

### API

* `POST /api/v1/mg/calculate` — validates inputs, returns breakdown and holds "deterministic_engine_id" for later contract creation.

### Data & contract creation

* `mg_proposals` (id, vehicle_id, proposal_json, monthly_mg, tenant_id, created_at)
* On acceptance: `mg_contracts` created (billing schedule, start_date, recurrence).

### Tests

* Deterministic engine unit tests with sample vehicles and expected outputs (assert exact numeric match).
* Regression no-LLM tests: ensure engine results don't change unless matrices updated.

---

# 4 — EKA Operator (Action Agent / Tool Executor)

### Purpose

* Translate natural language commands into **approved** internal tool calls (creates job cards, invoices, inventory changes, payments), performing required permission checks and confirmation step before irreversible DB writes.

### Architecture

* **Intent parser** (LLM or deterministic NLU) → **Tool mapper** → **Preview generator** → **Confirmation handler** → **Tool executor** (service layer) → **Audit log**.

### Safety flow (required)

1. Validate Domain Gate & Permission Gate.
2. Validate Context Gate: extract required params.
3. Produce **Action Preview** (structured JSON) and **explicit** statement:

   ```
   No irreversible action will be executed without explicit confirmation.
   Please confirm to proceed.
   ```
4. On user confirmation, call internal tool function (no direct SQL from LLM).
5. Log the tool execution with full payload in `audit_logs`.

### Exposed tools (examples)

* `create_job_card(vehicle_number, complaint, tenant_id)`
* `generate_invoice(job_card_id, tenant_id)`
* `create_mg_contract(vehicle_id, monthly_mg, tenant_id)` — only after MG proposal accepted and billing configured.
* `add_inventory(item_id, qty, tenant_id)`

### Example Operator endpoint

* `POST /api/v1/operator/execute` — request includes `intent`, `parsed_args`, `dry_run=true` → returns preview.
* `POST /api/v1/operator/confirm` — with preview_id & user confirmation → executes.

### Data models

* `operator_previews` (id, tenant_id, actor_id, tool_name, args_json, preview_json, created_at, expires_at)
* `operator_executions` (id, preview_id, execution_result, created_at)

### Tests

* End-to-end operator tasks with role matrix: ensure unauthorized role cannot confirm.
* Audit trail tests: every execution references a preview.

---

# 5 — EKA Dashboard (Insight Layer)

### Purpose

* Read-only BI layer; role-specific KPIs and trend analyses, driven from operational DB.

### Views & KPIs

* **Workshop**: revenue, gross margin, jobs by state, pending approvals, low stock alerts.
* **Fleet**: MG commitments vs actual spend, cost per vehicle, downtime metrics.
* **Owner**: per vehicle service history, upcoming service due.

### Implementation notes

* Backend: analytic microservice(s) or read replicas for heavy aggregations.
* Materialized views for expensive queries (refresh schedule).
* Pre-aggregations stored in `analytics.*` tables for dashboard panels.

### AI augmented insights (read-only)

* Optionally, EKA Chat can generate natural language summaries for dashboards ("Revenue up 12% MoM"). These are **advisory only** and logged.

### Tests

* Snapshot tests for dashboards after simulated job flows (validate aggregations).

---

# Pricing & Monetization — how pricing is linked across models

### Pricing primitives

* **Catalogs** (source of truth):

  * `catalog.parts` (part_id, part_code, description, base_price, hsn_code, gst_rate, tenant_specific_markup?)
  * `catalog.labor_rates` (task_code, base_minutes, labor_fee, city_modifier)
  * `catalog.city_index` (city_code, labor_multiplier)

* **Subscription plans** (per tenant):

  * `plans` (plan_code, monthly_fee, chat_quota, operator_quota, includes_mg, dashboard_tier)

* **Usage metering**

  * `usage_events` (tenant_id, event_type: CHAT_TOKEN, OPERATOR_ACTION, MG_CALC, timestamp, units)
  * Billing engine aggregates usage vs plan quotas monthly.

### How pricing flows into features

* **Job Flow → Estimate → Invoice**

  * Parts price retrieved from `catalog.parts`
  * Labor price: `base_labor` × `city_index` × `tenant_markup` (if any)
  * Line taxes computed by HSN / GST rate from part entry — deterministic code, stored in invoice lines.
* **EKA-MG**

  * MG uses `wear_matrix` + city index + risk multiplier → outputs monthly_mg. That monthly value is contractually charged by the workshop to the customer — platform may enable billing or simply record contract.
* **Operator quotas**

  * Each use of an Operator tool increments operator_quota. If quotas exhausted, platform returns plan upgrade message.
* **Chat quota**

  * Each LLM call consumes tokens; token accounting stored in `usage_events`. Overages trigger top-up billing/upgrade.

### Billing & invoicing flows

* `invoice` created from job flow includes GST tax split and totals. For platform revenue: subscription invoices for tenant billed monthly (platform → workshop).
* MG contracts produce recurring charges scheduled by `billing_scheduler`.

---

# Security, Multi-Tenant & Audit

### Tenant isolation

* Every table includes `tenant_id` (UUID). Row-Level Security (Postgres RLS) enforces that `current_setting('eka.tenant')` is applied to all queries.
* Service layer uses `tenant_id` from auth token to set DB session parameter.

### Auth & RBAC

* OAuth/OIDC for login; JWT for API calls.
* Fine-grained permissions: `can_create_invoice`, `can_confirm_operator_action`, `can_change_pricing` etc.

### Audit & immutability

* `audit_logs` is append-only; use a separate audit schema and restricted permissions.
* Changes to critical tables (catalog, pricing_matrices) require role check and are recorded with previous snapshot.

---

# Observability, SRE & Deployment

### Logging & metrics

* Structured logs (JSON) with correlation_id.
* Prometheus metrics: request latency, job_flow_state_counts, mg_engine_calls, operator_failures, token_usage.
* Sentry for errors.

### Caching & rate limiting

* Redis caches catalog lookups and city multipliers.
* Rate limiting per tenant (Redis token bucket).

### Deploy

* Docker + Kubernetes (recommend autoscaling for LLM proxy + worker pods)
* Managed Postgres, Redis, and Vector DB (pgvector).
* Secrets in vault (GEMINI_API_KEY, DB_URL).

---

# Test strategy & QA

1. **Unit tests**: governance gates, deterministic math, FSM transitions.
2. **Integration tests**: operator preview + confirm flows, MG proposals → contract creation.
3. **E2E**: synthetic tenant runs full job → invoice → dashboard.
4. **Security tests**: RLS bypass attempts, role privilege checks.
5. **Load tests**: simulate chat/agent bursts to size LLM proxy & worker pools.

---

# Production-ready repo structure (copy/paste friendly)

```
eka-ai-platform/
├── app/
│   ├── main.py                          # FastAPI entrypoint (sets tenant context, includes routers)
│   ├── core/
│   │   ├── config.py                    # pydantic settings, env loading
│   │   ├── security.py                  # auth helpers, RBAC
│   │   ├── middleware.py                # tenant middleware, logging
│   │   └── dependencies.py              # fastapi deps (db, current_user)
│   ├── ai/
│   │   ├── system_prompt.py             # EKA constitution strings & helpers
│   │   ├── gemini_client.py             # async Gemini wrapper + streaming helpers
│   │   ├── tool_registry.py             # declarations of available operator tools
│   │   └── governance.py                # Domain/Permission/Context/Confidence gate logic
│   ├── modules/
│   │   ├── job_cards/
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── schema.py                 # pydantic request/response
│   │   │   └── model.py                  # sqlalchemy models
│   │   ├── invoices/
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── schema.py
│   │   │   └── model.py
│   │   ├── mg_engine/
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── deterministic_engine.py   # pure math, unit-tested
│   │   │   └── schema.py
│   │   ├── operator/
│   │   │   ├── router.py
│   │   │   ├── tool_handler.py           # preview -&gt; confirm -&gt; execute
│   │   │   └── schema.py
│   │   └── dashboard/
│   │       ├── router.py
│   │       └── analytics_service.py
│   ├── db/
│   │   ├── session.py                    # async engine, sessionmaker
│   │   ├── base.py                       # declarative base with tenant mixin
│   │   └── models.py                     # shared models
│   └── utils/
│       ├── logger.py
│       ├── validators.py
│       └── tests_helpers.py
├── migrations/                           # alembic
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── .env.example
├── requirements.txt
├── ARCHITECTURE.md
└── README.md
```

---

# Example JSONs & function signatures (copy-paste)

**Create job card preview (Operator preview payload)**

```json
POST /api/v1/operator/execute
{
  "intent": "create_job_card",
  "args": {"vehicle_number":"MH12AB1234","complaint":"brake issue"},
  "tenant_id":"tenant-uuid",
  "actor_id":"user-uuid",
  "dry_run": true
}
```

**Response (preview)**

```json
{
  "preview_id":"preview-uuid",
  "tool":"create_job_card",
  "args":{"vehicle_number":"MH12AB1234","complaint":"brake issue"},
  "action_preview":"A new job card will be created for MH12AB1234 with complaint 'brake issue'. No irreversible action will be executed without explicit confirmation. Please confirm to proceed.",
  "expires_at":"2026-03-01T12:00:00Z"
}
```

**Confirm execution**

```json
POST /api/v1/operator/confirm
{
  "preview_id":"preview-uuid",
  "confirm": true,
  "actor_id":"user-uuid"
}
```

**MG Calculate request**

```json
POST /api/v1/mg/calculate
{
  "make":"Tata","model":"Nexon","year":2021,"fuel_type":"diesel",
  "city":"Mumbai","monthly_km":2500,"warranty_status":"out_of_warranty",
  "usage_type":"commercial","tenant_id":"tenant-uuid"
}
```

**MG response (deterministic)**

```json
{
  "annual_parts": 48000,
  "annual_labor": 24000,
  "city_adj": 1.15,
  "risk_adj": 1.10,
  "final_annual_cost": 92400,
  "monthly_mg": 7700,
  "notes": "Final MG calculation must be executed by deterministic financial engine. AI cannot compute financial projections directly."
}
```

---

# CI / CD & release checklist

1. PR template requires: unit tests, lint (ruff/black), security scan (safety/bandit), schema migration (alembic).
2. CI pipeline stages: lint → unit tests → integration tests (.env.example
├── requirements.txt
├── ARCHITECTURE.md
└── README.md
```

---

# Example JSONs & function signatures (copy-paste)

**Create job card preview (Operator preview payload)**

```json
POST /api/v1/operator/execute
{
  "intent": "create_job_card",
  "args": {"vehicle_number":"MH12AB1234","complaint":"brake issue"},
  "tenant_id":"tenant-uuid",
  "actor_id":"user-uuid",
  "dry_run": true
}
```

**Response (preview)**

```json
{
  "preview_id":"preview-uuid",
  "tool":"create_job_card",
  "args":{"vehicle_number":"MH12AB1234","complaint":"brake issue"},
  "action_preview":"A new job card will be created for MH12AB1234 with complaint 'brake issue'. No irreversible action will be executed without explicit confirmation. Please confirm to proceed.",
  "expires_at":"2026-03-01T12:00:00Z"
}
```

**Confirm execution**

```json
POST /api/v1/operator/confirm
{
  "preview_id":"preview-uuid",
  "confirm": true,
  "actor_id":"user-uuid"
}
```

**MG Calculate request**

```json
POST /api/v1/mg/calculate
{
  "make":"Tata","model":"Nexon","year":2021,"fuel_type":"diesel",
  "city":"Mumbai","monthly_km":2500,"warranty_status":"out_of_warranty",
  "usage_type":"commercial","tenant_id":"tenant-uuid"
}
```

**MG response (deterministic)**

```json
{
  "annual_parts": 48000,
  "annual_labor": 24000,
  "city_adj": 1.15,
  "risk_adj": 1.10,
  "final_annual_cost": 92400,
  "monthly_mg": 7700,
  "notes": "Final MG calculation must be executed by deterministic financial engine. AI cannot compute financial projections directly."
}
```

---

# CI / CD & release checklist

1. PR template requires: unit tests, lint (ruff/black), security scan (safety/bandit), schema migration (alembic).
2. CI pipeline stages: lint → unit tests → integration tests (docker compose) → build image → push to registry.
3. CD: tag release → deploy to staging → smoke tests → promote to prod.
4. Secrets: stored in secrets manager; GEMINI key rotated regularly.

---

# Monitoring & SLAs (production considerations)

* SLOs: API P95 latency &lt; 300ms (non-LLM endpoints); LLM calls SLO based on external provider SLA.
* Alerts:

  * Failed deterministic engine runs.
  * Unauthorized operator confirmations attempted.
  * RLS violations.
* Backups: daily DB backups, hourly WAL archiving.

---

# Migration & data import guidance (from legacy)

* Migrate `catalog.parts` first and run reconciliation scripts to ensure HSN/GST fields present.
* Backfill `tenant_id` and enable RLS in maintenance window.
* Validate deterministic MG outputs on a sample fleet (compare to historical costs).

---

# Final notes — governance & product controls

* **Always** show previews before irreversible actions.
* **Never** allow LLM to compute GST or MG math; these are deterministic backend routines.
* Confidence gating must be tested with adversarial inputs.
* Pricing changes require dual-approval & audit record.
