# PRE-DEPLOYMENT CHECKLIST: EKA-AI MVP v1.0.0

The following tasks must be independently verified and cross-checked before declaring the V1 instance production-ready and issuing the final switch-over.

## 🧰 1. Core Prerequisites & Dependencies
- [x] Verify `pytest-mock` is strictly installed in production/CI environment to run all AI governance and boundary tests.
- [x] Ensure CI environment holds all standard environment variables listed in `.env.example` directly via `pydantic-settings`.
- [ ] Confirm AWS S3 Buckets are provisioned (ap-south-1) with 24-hr expiry policy keys setup.
- [ ] Secure IAM credentials generated solely for S3 pre-signed URL bounds without broad access rights.
- [ ] Ensure Redis cluster is scaled for per-minute rate limit caching and tracking multi-tenant degraded modes smoothly.
- [ ] Ensure RabbitMQ paths for `/usage.events` and `/notifications` are successfully bound to corresponding Queues.
- [ ] Setup Twilio SMS templates and Sendgrid domain key mappings for `noreply@go4garage.in` email bounds.
- [ ] Procure `Gemini 2.0`, `OpenAI`, and `Anthropic` API Keys securely pinned inside Kubernetes cluster secrets.

## 🚦 2. Test Suite & Coverage 
- [x] Clear out empty, cheating proxy methods inside legacy `.py` files to assure accurate, native metrics evaluations.
- [x] Verify API mock routing paths are not bypassing internal `context_gate` criteria accidentally generating false positives.
- [ ] Ensure `100%` Coverage threshold applies firmly across all Core Engines:
    - `mg_engine` (Fully passing 15/15 unit bounds)
    - `governance_gates` (Fully passing 15/15 unit bounds)
    - `fastapi state_machine` (Fully passing 16/16 unit bounds)
- [ ] Mock the asynchronous execution loops on `test_vehicle_service` correctly injecting internal `AsyncSessionLocal` payloads.

## 🔐 3. Security Hardening
- [x] PostgreSQL RLS Enabled securely across all tables filtering automatically by `app.current_tenant` context injections.
- [x] Confirm `Audit Logs` are locked firmly restricting `UPDATE` or `DELETE` commands purely to SQL constraints triggers.
- [ ] Validate standard CSRF/CORS mappings isolating requests across the Starlette configuration properly preventing script injections. 

## ⚖️ 4. AI & Regulatory Adjustments
- [x] Run routine audits on `LLMClient` verifying the explicit fallback mechanism correctly cascades 10.0s time-outs from Google -> OpenAI -> Anthropic.
- [x] Ensure Data Privacy `/export` and `/delete` endpoints accurately hash specific fields to SHA-256 formats mitigating potential regulatory fines dynamically.

## 🚀 5. Final Switch-Over
1. [ ] Suspend legacy V0 operations tracking and switch global DNS targets to `.eka-ai.com/api/v1/`.
2. [ ] Inject first `alembic upgrade head` across the fresh AWS RDS environments mapping 0010 - 0014 dynamically. 
3. [ ] Trigger `system.alerts` confirming degraded modes are natively deactivated across the active nodes. 

Proceed once verified. 
