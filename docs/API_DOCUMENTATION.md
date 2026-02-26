# EKA-AI Platform API Documentation

> **For Frontend Developers** - Complete API reference with examples

## Base URL

```
Development: http://localhost:8000
Staging:     https://staging-api.eka-ai.com
Production:  https://api.eka-ai.com
```

## Authentication

All endpoints (except root and examples) require Bearer token authentication:

```http
Authorization: Bearer fake-super-secret-token
```

**Note**: In production, use a valid JWT from your OAuth provider.

---

## 1. Chat API

### POST `/api/v1/chat/query`

Send a diagnostic query to EKA-AI. The system will validate through governance gates and return a structured diagnostic response.

#### Request

```json
{
  "query": "Brake grinding noise when stopping",
  "vehicle": {
    "make": "Maruti",
    "model": "Swift",
    "year": 2019,
    "fuel": "petrol"
  },
  "tenant_id": "tenant_123"
}
```

#### Response (Success - 200)

```json
{
  "issue_summary": "A grinding noise is heard when the brakes are applied.",
  "probable_causes": [
    "Severely Worn Brake Pads: The friction material may be completely worn",
    "Damaged or Scored Brake Rotors: Grooved or warped rotors",
    "Foreign Object: Stone or debris lodged between pad and rotor",
    "Sticking Brake Caliper: Caliper not releasing properly"
  ],
  "diagnostic_steps": [
    "Visual Inspection of Brake System: Check pad thickness and rotor condition",
    "Check for Foreign Debris: Look between pad and rotor",
    "Assess Pad Wear Indicators: Check metal wear indicators",
    "Test Caliper Movement: Verify wheels rotate freely when lifted",
    "Listen for Noise Characteristics: Note if consistent or intermittent"
  ],
  "safety_advisory": "A grinding noise indicates critical brake system issue. Driving is unsafe. Have inspected by qualified mechanic immediately.",
  "confidence_level": 95.0,
  "rag_references": null
}
```

#### Error Responses

**Domain Gate Deny (403)**
```json
{
  "detail": "DOMAIN_GATE_DENY: Query is not related to automobiles."
}
```

**Context Request (422)**
```json
{
  "detail": "CONTEXT_REQUEST: Please provide vehicle make, model, and year for a better diagnosis."
}
```

**Low Confidence (422)**
```json
{
  "detail": "REQUEST_CLARIFICATION: Confidence level is below threshold. Please provide more details."
}
```

---

### GET `/api/v1/chat/examples`

Get example queries for UI demonstration.

#### Response (200)

```json
{
  "example1": {
    "query": "My car is making a grinding noise when I brake.",
    "vehicle": {
      "make": "Maruti",
      "model": "Swift",
      "year": 2019,
      "fuel": "petrol"
    }
  },
  "example2": {
    "query": "What are the common causes of engine overheating?"
  }
}
```

---

## 2. Job Cards API

### POST `/api/v1/job-cards`

Create a new job card (main service request).

#### Request

```json
{
  "vehicle_id": 1,
  "complaint": "Brake grinding noise",
  "state": "OPEN"
}
```

#### Response (200)

```json
{
  "id": 1,
  "vehicle_id": 1,
  "complaint": "Brake grinding noise",
  "state": "OPEN",
  "tenant_id": "some_tenant_id",
  "job_no": "JB-0001",
  "created_at": "2026-02-24T07:59:07.853127",
  "created_by": "user@example.com"
}
```

---

### GET `/api/v1/job-cards/{job_card_id}`

Get a specific job card by ID.

#### Response (200)

```json
{
  "id": 1,
  "vehicle_id": 1,
  "complaint": "Brake grinding noise",
  "state": "OPEN",
  "tenant_id": "some_tenant_id",
  "job_no": "JB-0001",
  "created_at": "2026-02-24T07:59:07.853127",
  "created_by": "user@example.com"
}
```

---

### PATCH `/api/v1/job-cards/{job_card_id}/transition`

Transition job card to a new state (FSM operation).

#### Request

```json
{
  "new_state": "DIAGNOSIS"
}
```

**Valid Transitions**:
- `OPEN` → `DIAGNOSIS`, `CANCELLED`
- `DIAGNOSIS` → `ESTIMATE_PENDING`, `CANCELLED`
- `ESTIMATE_PENDING` → `APPROVAL_PENDING`, `CANCELLED`
- `APPROVAL_PENDING` → `APPROVED`, `REJECTED`
- `APPROVED` → `REPAIR`, `CANCELLED`
- `REPAIR` → `QC_PDI`, `CANCELLED`
- `QC_PDI` → `READY`, `REPAIR` (if failed)
- `READY` → `INVOICED`
- `INVOICED` → `PAID`, `CANCELLED`
- `PAID` → `CLOSED`

#### Response (200)

Same as GET response with updated `state`.

#### Error Response (400)

```json
{
  "detail": "Invalid state transition from OPEN to REPAIR"
}
```

---

### POST `/api/v1/job-cards/{job_card_id}/estimate`

Create an estimate for a job card.

#### Request

```json
{
  "job_id": 1,
  "lines": [
    {
      "part_id": 101,
      "quantity": 2,
      "price": 2500.00,
      "tax_rate": 0.18
    },
    {
      "part_id": 102,
      "quantity": 1,
      "price": 1500.00,
      "tax_rate": 0.18
    }
  ]
}
```

#### Response (200)

```json
{
  "id": 1,
  "job_id": 1,
  "lines": [
    {
      "part_id": 101,
      "quantity": 2,
      "price": 2500.00,
      "tax_rate": 0.18
    }
  ],
  "total_parts": 5000.00,
  "total_labor": 2000.00,
  "tax_breakdown": {
    "gst_18": 1260.00,
    "total": 8260.00
  }
}
```

---

## 3. MG Engine API

### POST `/api/v1/mg/calculate`

Calculate Maintenance Guarantee (MG) subscription cost.

#### Request

```json
{
  "make": "Tata",
  "model": "Nexon",
  "year": 2021,
  "fuel_type": "diesel",
  "city": "Mumbai",
  "monthly_km": 2500,
  "warranty_status": "out_of_warranty",
  "usage_type": "commercial",
  "tenant_id": "tenant_123"
}
```

**Enums**:
- `fuel_type`: `petrol`, `diesel`, `electric`, `hybrid`
- `warranty_status`: `under_warranty`, `out_of_warranty`
- `usage_type`: `personal`, `commercial`

#### Response (200)

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

**Note**: All financial calculations are deterministic - no AI math.

---

## 4. Operator API

### POST `/api/v1/operator/execute`

Execute a tool with preview (dry run). Always generates a preview first.

#### Request

```json
{
  "intent": "create_job_card",
  "args": {
    "vehicle_number": "MH12AB1234",
    "complaint": "Brake issue"
  },
  "tenant_id": "tenant_123",
  "actor_id": "user_456",
  "dry_run": true
}
```

#### Response (200)

```json
{
  "preview_id": "550e8400-e29b-41d4-a716-446655440000",
  "tool": "create_job_card",
  "args": {
    "vehicle_number": "MH12AB1234",
    "complaint": "Brake issue"
  },
  "action_preview": "A new job card will be created for MH12AB1234 with complaint 'Brake issue'. No irreversible action will be executed without explicit confirmation. Please confirm to proceed.",
  "expires_at": "2026-02-24T08:15:00Z"
}
```

---

### POST `/api/v1/operator/confirm`

Confirm and execute a previously generated preview.

#### Request

```json
{
  "preview_id": "550e8400-e29b-41d4-a716-446655440000",
  "confirm": true,
  "actor_id": "user_456"
}
```

#### Response (200) - Success

```json
{
  "execution_id": "660e8400-e29b-41d4-a716-446655440001",
  "status": "success",
  "result": {
    "job_card_id": 2
  }
}
```

#### Response (200) - Cancelled

```json
{
  "execution_id": null,
  "status": "cancelled",
  "result": {
    "message": "Action not confirmed."
  }
}
```

#### Error Response (400)

```json
{
  "detail": "Preview not found or expired."
}
```

---

## 5. Dashboard API

### GET `/api/v1/dashboard/{dashboard_type}`

Get dashboard metrics (read-only).

**Types**: `workshop`, `fleet`, `owner`

#### Response (200) - Workshop Dashboard

```json
{
  "type": "workshop",
  "kpis": {
    "revenue_today": 125000,
    "revenue_mtd": 2850000,
    "jobs_in_progress": 12,
    "pending_approvals": 3,
    "avg_job_value": 8500
  },
  "job_state_counts": {
    "OPEN": 5,
    "DIAGNOSIS": 3,
    "REPAIR": 4,
    "READY": 2
  }
}
```

---

## Error Response Formats

### 400 Bad Request
```json
{
  "detail": "Invalid request payload"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "The user does not have the required permission"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "vehicle", "year"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Frontend Integration Examples

### React Hook Example

```typescript
// hooks/useEKAChat.ts
import { useState } from 'react';

interface ChatRequest {
  query: string;
  vehicle?: {
    make: string;
    model: string;
    year: number;
    fuel?: string;
  };
  tenant_id: string;
}

interface ChatResponse {
  issue_summary: string;
  probable_causes: string[];
  diagnostic_steps: string[];
  safety_advisory: string;
  confidence_level: number;
}

export const useEKAChat = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendQuery = async (request: ChatRequest): Promise<ChatResponse | null> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/v1/chat/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(request)
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Request failed');
      }

      return await response.json();
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  };

  return { sendQuery, loading, error };
};
```

### Vue Composable Example

```typescript
// composables/useJobCards.ts
import { ref } from 'vue';

export const useJobCards = () => {
  const jobCard = ref(null);
  const loading = ref(false);

  const createJobCard = async (data: {
    vehicle_id: number;
    complaint: string;
  }) => {
    loading.value = true;
    const response = await fetch('/api/v1/job-cards', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(data)
    });
    jobCard.value = await response.json();
    loading.value = false;
    return jobCard.value;
  };

  const transitionState = async (jobId: number, newState: string) => {
    const response = await fetch(`/api/v1/job-cards/${jobId}/transition`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({ new_state: newState })
    });
    return await response.json();
  };

  return { jobCard, loading, createJobCard, transitionState };
};
```

---

## WebSocket Events (Future)

Real-time updates for job state changes:

```javascript
const ws = new WebSocket('wss://api.eka-ai.com/ws/job-cards');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // { type: 'JOB_STATE_CHANGED', job_id: 1, old_state: 'OPEN', new_state: 'DIAGNOSIS' }
};
```

---

## Support

- **API Issues**: Contact backend team
- **Documentation**: Submit PR to update this file
- **Examples**: See `tests/e2e/` for full integration tests
