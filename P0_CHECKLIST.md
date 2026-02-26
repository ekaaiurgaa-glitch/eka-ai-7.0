# P0 Critical Fixes Checklist
## Production Deployment Blockers

---

## FIX 1: Add `variant` Field to Vehicle Model

### Database
- [ ] Update `app/modules/vehicles/model.py` - Add `variant` column
- [ ] Update `app/modules/vehicles/schema.py` - Add to VehicleBase schema
- [ ] Update `app/modules/mg_engine/schema.py` - Add to MGCalculationRequest
- [ ] Create Alembic migration for database schema change
- [ ] Run migration: `alembic upgrade head`

### Backend API
- [ ] Update vehicle CRUD operations to handle variant field
- [ ] Update MG calculation service to use variant in wear matrix lookup

### Frontend
- [ ] Update `frontend/src/pages/VehiclesPage.jsx` - Add variant input field
- [ ] Update `frontend/src/pages/MGPage.jsx` - Add variant dropdown/input
- [ ] Add variant display in vehicle list cards

### Data Seeding
- [ ] Seed wear matrix data with variant-specific parts costs
- [ ] Verify variant lookup works in MG calculations

### Testing
- [ ] Can create vehicle with variant
- [ ] Can view vehicle variant in list
- [ ] MG calculation accepts and uses variant field
- [ ] Database migration runs without errors
- [ ] Existing vehicles work without variant (nullable field)

---

## FIX 2: Implement Job Card State Transition UI

### New Components
- [ ] Create `frontend/src/components/JobCardStateTransition.jsx`
- [ ] Create `frontend/src/components/JobStateBadge.jsx` (reusable status display)
- [ ] Create `frontend/src/pages/JobCardDetailPage.jsx`

### Frontend Routing
- [ ] Update `frontend/src/App.jsx` - Add route `/jobs/:jobId`
- [ ] Update `frontend/src/pages/JobsPage.jsx` - Make rows clickable

### State Transition Logic
- [ ] Implement `VALID_TRANSITIONS` constant (all 11 states)
- [ ] Implement `STATE_CONFIG` with colors and labels
- [ ] Create transition validation (prevent invalid moves)
- [ ] Handle validation errors (e.g., need estimate before REPAIR)

### API Integration
- [ ] Connect to `PATCH /api/v1/job-cards/{id}/transition`
- [ ] Handle 400 errors (invalid transition)
- [ ] Handle 202 errors (requires approval)
- [ ] Refresh job data after successful transition

### UI Features
- [ ] Show current state with color badge
- [ ] Dropdown of valid next states only
- [ ] Arrow icon between states
- [ ] Confirmation before transition
- [ ] Loading state during API call
- [ ] Error display

### State Validation Rules Display
- [ ] Show "ℹ️ Requires approved estimate" for REPAIR transition
- [ ] Show "ℹ️ Will generate invoice" for INVOICED transition
- [ ] Show "ℹ️ Final state" for CLOSED/CANCELLED

### Testing
- [ ] Can view job card detail page
- [ ] Valid transitions shown for each state
- [ ] Invalid transitions blocked
- [ ] State change persists after refresh
- [ ] Audit log captures transitions
- [ ] Error messages clear and helpful

---

## FIX 3: Implement Estimate Creation UI

### New Components
- [ ] Create `frontend/src/components/EstimateForm.jsx`
- [ ] Create `frontend/src/components/EstimateLineItem.jsx` (for each row)

### Backend Schema (Verify Exists)
- [ ] Confirm `Estimate` model in `app/modules/job_cards/model.py`
- [ ] Confirm `EstimateCreate` schema
- [ ] Confirm `POST /api/v1/job-cards/{id}/estimate` endpoint

### Frontend Form Features
- [ ] Dynamic part line items (add/remove)
- [ ] Fields per line: Description, Qty, Price, Tax Rate
- [ ] GST rate dropdown: 5%, 12%, 18%, 28%
- [ ] Real-time line total calculation
- [ ] Labor hours input
- [ ] Labor rate input (default from catalog)
- [ ] Real-time labor subtotal

### Calculations
- [ ] Parts subtotal = Σ(price × quantity)
- [ ] Labor subtotal = hours × rate
- [ ] Tax per line = price × quantity × tax_rate
- [ ] Total GST = Σ(tax per line)
- [ ] Grand total = parts + labor + total GST

### API Integration
- [ ] Connect to `POST /api/v1/job-cards/{id}/estimate`
- [ ] Handle validation errors
- [ ] Refresh job data after creation
- [ ] Show success confirmation

### UI Layout
- [ ] Card container with title
- [ ] Parts section with add/remove buttons
- [ ] Labor section separate
- [ ] Totals summary box with breakdown
- [ ] Create Estimate button (disabled if invalid)
- [ ] Cancel button

### Validation
- [ ] Description required for each line
- [ ] Price > 0 for each line
- [ ] Quantity > 0 for each line
- [ ] At least one part line OR labor hours > 0

### Testing
- [ ] Can add multiple part lines
- [ ] Can remove part lines
- [ ] GST calculated correctly per line
- [ ] Labor added to total
- [ ] Real-time totals update
- [ ] Estimate linked to job card
- [ ] Cannot transition to REPAIR without approved estimate

---

## FIX 4: Connect Backend APIs (Remove Mock Data)

### Invoices Module

#### Backend (Create if missing)
- [ ] Create `app/modules/invoices/model.py` - Invoice & InvoiceLine models
- [ ] Create `app/modules/invoices/schema.py` - Pydantic schemas
- [ ] Create `app/modules/invoices/service.py` - Business logic
- [ ] Create `app/modules/invoices/router.py` - API endpoints
- [ ] Create Alembic migration for invoice tables

#### API Endpoints Required
- [ ] `GET /api/v1/invoices` - List invoices
- [ ] `POST /api/v1/invoices` - Create invoice from job
- [ ] `GET /api/v1/invoices/{id}` - Get invoice details
- [ ] `POST /api/v1/invoices/{id}/pay` - Mark as paid
- [ ] `GET /api/v1/invoices/{id}/pdf` - Download PDF

#### Frontend Updates
- [ ] Update `frontend/src/pages/InvoicesPage.jsx`:
  - [ ] Replace `MOCK_INVOICES` with API call
  - [ ] Implement `fetchInvoices()` function
  - [ ] Implement `generateInvoice(jobId)` function
  - [ ] Implement `markAsPaid(invoiceId)` function
  - [ ] Implement `downloadPDF(invoiceId)` function
  - [ ] Add loading states
  - [ ] Add error handling
  - [ ] Refresh list after actions

### Approvals Module

#### Backend
- [ ] Verify `GET /api/v1/approvals` endpoint exists
- [ ] Verify approval workflow API endpoints

#### Frontend Updates
- [ ] Update `frontend/src/pages/ApprovalsPage.jsx`:
  - [ ] Replace mock approvals with API call
  - [ ] Implement `fetchApprovals()` function
  - [ ] Implement `approve(approvalId, comment)` function
  - [ ] Implement `reject(approvalId, reason)` function
  - [ ] Refresh list after actions

### Dashboard Module

#### Backend
- [ ] Verify `GET /api/v1/dashboards/workshop` endpoint
- [ ] Ensure KPI calculations work with real data

#### Frontend Updates
- [ ] Update `frontend/src/pages/DashboardPage.jsx`:
  - [ ] Replace mock KPIs with API call
  - [ ] Implement `fetchDashboardData()` function
  - [ ] Handle loading states
  - [ ] Handle empty data state
  - [ ] Auto-refresh every 5 minutes

### Operator Module

#### Frontend Updates
- [ ] Update `frontend/src/pages/OperatorPage.jsx`:
  - [ ] Connect action forms to real API
  - [ ] Implement `executeOperatorAction()` function
  - [ ] Implement `confirmOperatorAction()` function
  - [ ] Show real preview from API
  - [ ] Handle execution result
  - [ ] Update usage tracking after execution

### Chat Module

#### Frontend Updates
- [ ] Update `frontend/src/pages/ChatPage.jsx`:
  - [ ] Verify chat API connection
  - [ ] Add token usage tracking display
  - [ ] Show RAG references if returned

### Testing API Integration
- [ ] Invoices load from database
- [ ] Can generate invoice from READY job
- [ ] Can mark invoice as paid
- [ ] Approvals load from database
- [ ] Can approve/reject with comments
- [ ] Dashboard shows real KPIs
- [ ] Operator actions execute via API
- [ ] Usage limits enforced after actions
- [ ] Error messages from API shown to user
- [ ] Loading states prevent double-clicks

---

## Cross-Cutting Concerns

### Error Handling (All Fixes)
- [ ] Network errors show retry option
- [ ] 401 errors redirect to login
- [ ] 403 errors show permission message
- [ ] 422 errors show validation details
- [ ] 500 errors show generic error message
- [ ] All errors logged to console

### Loading States (All Fixes)
- [ ] Buttons disabled during API calls
- [ ] Loading spinners on async actions
- [ ] Skeleton screens for data loading
- [ ] Progress indicators for multi-step operations

### Permission Checks (All Fixes)
- [ ] UI hides actions user cannot perform
- [ ] API calls include auth token
- [ ] Backend verifies permissions
- [ ] Graceful handling of permission denied

### Audit Trail (All Fixes)
- [ ] All create operations logged
- [ ] All state changes logged
- [ ] All approval actions logged
- [ ] Actor ID captured in logs
- [ ] Timestamps accurate

---

## Final Integration Testing

### End-to-End Flow 1: Job Card Creation
- [ ] Create vehicle with variant
- [ ] Create job card for vehicle
- [ ] Add estimate with parts and labor
- [ ] Approve estimate
- [ ] Transition to REPAIR
- [ ] Transition to QC_PDI
- [ ] Transition to READY
- [ ] Generate invoice
- [ ] Mark invoice as paid
- [ ] Verify job state is CLOSED

### End-to-End Flow 2: MG Calculation
- [ ] Create vehicle with all fields
- [ ] Go to MG Calculator
- [ ] Enter vehicle details
- [ ] Get accurate MG calculation
- [ ] Verify parts breakdown shown
- [ ] Save proposal (if implemented)

### End-to-End Flow 3: Operator AI
- [ ] Use natural language (if intent parser ready)
- [ ] Or fill form manually
- [ ] Generate preview
- [ ] Confirm action
- [ ] Verify job created
- [ ] Check usage incremented

### Performance Checks
- [ ] Page load < 3 seconds
- [ ] API response < 1 second
- [ ] No duplicate API calls
- [ ] Memory usage stable

---

## Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Backend Lead | | | |
| Frontend Lead | | | |
| QA Lead | | | |
| Product Owner | | | |

---

**Status:** ☐ Not Started | ☐ In Progress | ☐ Completed

**Completion Date:** ___________

**Verified By:** ___________
