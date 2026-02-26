# P0 Critical Fixes Plan
## Implementation Guide for Production-Ready EKA-AI

---

# FIX 1: Add `variant` Field to Vehicle Model

## Problem
Vehicle schema missing `variant` field required for accurate MG Engine calculations per BRD Section 3.

## Current State
```python
# app/modules/vehicles/schema.py
class VehicleBase(BaseModel):
    plate_number: str
    make: str
    model: str
    year: int
    fuel_type: FuelType
    # MISSING: variant
```

## Implementation Steps

### Step 1.1: Update Database Model
```python
# app/modules/vehicles/model.py
class Vehicle(Base, TenantMixin, TimestampMixin):
    __tablename__ = "vehicles"
    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String, index=True)
    make = Column(String, nullable=False)
    model = Column(String, nullable=False)
    variant = Column(String, nullable=True)  # NEW FIELD
    year = Column(Integer, nullable=False)
    fuel_type = Column(SAEnum(FuelTypeEnum), nullable=False)
    vin = Column(String, unique=True, index=True, nullable=True)
    owner_name = Column(String, nullable=True)
    monthly_km = Column(Integer, default=1000)
```

### Step 1.2: Update Pydantic Schemas
```python
# app/modules/vehicles/schema.py
class VehicleBase(BaseModel):
    plate_number: str
    make: str
    model: str
    variant: Optional[str] = None  # NEW FIELD
    year: int
    fuel_type: FuelType
    vin: Optional[str] = None
    owner_name: Optional[str] = None
    monthly_km: int = 1000
```

### Step 1.3: Create Alembic Migration
```bash
alembic revision -m "add_variant_to_vehicles"
```

Migration file:
```python
def upgrade():
    op.add_column('vehicles', sa.Column('variant', sa.String(), nullable=True))
    op.create_index('ix_vehicles_variant', 'vehicles', ['variant'])

def downgrade():
    op.drop_index('ix_vehicles_variant', table_name='vehicles')
    op.drop_column('vehicles', 'variant')
```

### Step 1.4: Update Frontend Form
```jsx
// frontend/src/pages/VehiclesPage.jsx
<div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
    <div><label>Plate Number *</label><input className="input" placeholder="KA-01-XX-1234" required /></div>
    <div><label>Make *</label><input className="input" placeholder="e.g. Maruti" required /></div>
    <div><label>Model *</label><input className="input" placeholder="e.g. Swift" required /></div>
    <div><label>Variant</label><input className="input" placeholder="e.g. VXI, ZXI+" /></div>  // NEW FIELD
    <div><label>Year *</label><input className="input" type="number" placeholder="2024" required /></div>
    <div><label>Fuel Type *</label>
        <select className="input" required>
            <option value="">Select...</option>
            <option value="petrol">Petrol</option>
            <option value="diesel">Diesel</option>
            <option value="electric">Electric</option>
            <option value="hybrid">Hybrid</option>
        </select>
    </div>
</div>
```

### Step 1.5: Update MG Engine Schema
```python
# app/modules/mg_engine/schema.py
class MGCalculationRequest(BaseModel):
    make: str
    model: str
    variant: Optional[str] = None  # NEW FIELD
    year: int
    fuel_type: FuelType
    city: str
    monthly_km: int = Field(..., gt=0)
    warranty_status: WarrantyStatus
    usage_type: UsageType
    tenant_id: Optional[str] = None
```

### Step 1.6: Update MG Page Frontend
```jsx
// frontend/src/pages/MGPage.jsx
<div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
    <div><label>Make *</label><input className="input" value={form.make} onChange={...} required /></div>
    <div><label>Model *</label><input className="input" value={form.model} onChange={...} required /></div>
    <div><label>Variant</label><input className="input" value={form.variant} onChange={...} placeholder="e.g. VXI" /></div>  // NEW
    <div><label>Year *</label><input className="input" type="number" value={form.year} onChange={...} required /></div>
    {/* ... rest of fields */}
</div>
```

---

# FIX 2: Implement Job Card State Transition UI

## Problem
Users cannot transition job cards through the workflow states (OPEN → DIAGNOSIS → REPAIR etc.).

## Current State
- Backend: `PATCH /api/v1/job-cards/{id}/transition` exists
- Frontend: No UI for state transitions

## Implementation Steps

### Step 2.1: Create State Transition Component
```jsx
// frontend/src/components/JobCardStateTransition.jsx
import { useState } from 'react';
import { ArrowRight, AlertCircle } from 'lucide-react';

const VALID_TRANSITIONS = {
    'OPEN': ['DIAGNOSIS', 'CANCELLED'],
    'DIAGNOSIS': ['ESTIMATE_PENDING', 'CANCELLED'],
    'ESTIMATE_PENDING': ['APPROVAL_PENDING', 'CANCELLED'],
    'APPROVAL_PENDING': ['APPROVED', 'REJECTED'],
    'APPROVED': ['REPAIR', 'CANCELLED'],
    'REPAIR': ['QC_PDI', 'CANCELLED'],
    'QC_PDI': ['READY', 'REPAIR'],
    'READY': ['INVOICED'],
    'INVOICED': ['PAID', 'CANCELLED'],
    'PAID': ['CLOSED'],
    'CLOSED': [],
    'CANCELLED': [],
    'REJECTED': []
};

const STATE_CONFIG = {
    'OPEN': { color: '#3b82f6', label: 'Open' },
    'DIAGNOSIS': { color: '#6366f1', label: 'Diagnosis' },
    'ESTIMATE_PENDING': { color: '#f59e0b', label: 'Estimate Pending' },
    'APPROVAL_PENDING': { color: '#f97316', label: 'Approval Pending' },
    'APPROVED': { color: '#22c55e', label: 'Approved' },
    'REPAIR': { color: '#8b5cf6', label: 'Repair' },
    'QC_PDI': { color: '#ec4899', label: 'QC/PDI' },
    'READY': { color: '#14b8a6', label: 'Ready' },
    'INVOICED': { color: '#0ea5e9', label: 'Invoiced' },
    'PAID': { color: '#10b981', label: 'Paid' },
    'CLOSED': { color: '#64748b', label: 'Closed' },
    'CANCELLED': { color: '#ef4444', label: 'Cancelled' },
    'REJECTED': { color: '#dc2626', label: 'Rejected' }
};

export default function JobCardStateTransition({ jobId, currentState, onTransition }) {
    const [selectedState, setSelectedState] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const allowedTransitions = VALID_TRANSITIONS[currentState] || [];

    const handleTransition = async () => {
        if (!selectedState) return;
        
        setLoading(true);
        setError(null);
        
        try {
            const token = localStorage.getItem('eka_token');
            const res = await fetch(`/api/v1/job-cards/${jobId}/transition`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ new_state: selectedState })
            });
            
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || 'Transition failed');
            }
            
            const updatedJob = await res.json();
            onTransition(updatedJob);
            setSelectedState('');
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    if (allowedTransitions.length === 0) {
        return (
            <div className="card" style={{ background: 'var(--bg-glass)' }}>
                <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '20px' }}>
                    Job card is in final state: <strong>{STATE_CONFIG[currentState]?.label}</strong>
                </div>
            </div>
        );
    }

    return (
        <div className="card">
            <div className="card__title">State Transition</div>
            
            {error && (
                <div style={{ 
                    background: 'rgba(239,68,68,0.1)', 
                    border: '1px solid rgba(239,68,68,0.3)',
                    borderRadius: 8,
                    padding: '12px',
                    marginBottom: '16px',
                    color: 'var(--danger)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                }}>
                    <AlertCircle size={16} />
                    {error}
                </div>
            )}
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '16px' }}>
                <div style={{ 
                    padding: '8px 16px', 
                    borderRadius: 8,
                    background: STATE_CONFIG[currentState]?.color + '20',
                    color: STATE_CONFIG[currentState]?.color,
                    fontWeight: 600
                }}>
                    {STATE_CONFIG[currentState]?.label}
                </div>
                <ArrowRight size={20} color="var(--text-muted)" />
                <select 
                    className="input" 
                    value={selectedState}
                    onChange={(e) => setSelectedState(e.target.value)}
                    style={{ minWidth: '200px' }}
                >
                    <option value="">Select next state...</option>
                    {allowedTransitions.map(state => (
                        <option key={state} value={state}>
                            {STATE_CONFIG[state]?.label}
                        </option>
                    ))}
                </select>
            </div>
            
            <button 
                className="btn btn--primary"
                onClick={handleTransition}
                disabled={!selectedState || loading}
            >
                {loading ? 'Transitioning...' : 'Transition State'}
            </button>
            
            {/* Validation Rules Display */}
            {(currentState === 'APPROVED' && !selectedState) && (
                <div style={{ marginTop: '12px', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                    ℹ️ Transition to REPAIR requires an approved estimate
                </div>
            )}
            {(currentState === 'READY' && !selectedState) && (
                <div style={{ marginTop: '12px', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                    ℹ️ Transition to INVOICED will generate an invoice
                </div>
            )}
        </div>
    );
}
```

### Step 2.2: Create Job Card Detail Page
```jsx
// frontend/src/pages/JobCardDetailPage.jsx
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import JobCardStateTransition from '../components/JobCardStateTransition';
import EstimateForm from '../components/EstimateForm';

export default function JobCardDetailPage() {
    const { jobId } = useParams();
    const navigate = useNavigate();
    const [job, setJob] = useState(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('details');

    useEffect(() => {
        fetchJobDetails();
    }, [jobId]);

    const fetchJobDetails = async () => {
        try {
            const token = localStorage.getItem('eka_token');
            const res = await fetch(`/api/v1/job-cards/${jobId}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (!res.ok) throw new Error('Failed to fetch job');
            const data = await res.json();
            setJob(data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div>Loading...</div>;
    if (!job) return <div>Job card not found</div>;

    return (
        <div className="fade-in">
            <div className="main__header">
                <h2>Job Card {job.job_no}</h2>
                <button className="btn btn--ghost" onClick={() => navigate('/app/jobs')}>
                    ← Back to List
                </button>
            </div>

            {/* Tabs */}
            <div style={{ display: 'flex', gap: '8px', marginBottom: '24px' }}>
                {['details', 'transition', 'estimate', 'history'].map(tab => (
                    <button
                        key={tab}
                        className={`btn ${activeTab === tab ? 'btn--primary' : 'btn--ghost'}`}
                        onClick={() => setActiveTab(tab)}
                    >
                        {tab.charAt(0).toUpperCase() + tab.slice(1)}
                    </button>
                ))}
            </div>

            {/* Tab Content */}
            {activeTab === 'details' && (
                <div className="card">
                    <div className="card__title">Job Details</div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                        <div><strong>Job Number:</strong> {job.job_no}</div>
                        <div><strong>Status:</strong> {job.state}</div>
                        <div><strong>Vehicle ID:</strong> {job.vehicle_id}</div>
                        <div><strong>Created:</strong> {new Date(job.created_at).toLocaleString()}</div>
                        <div style={{ gridColumn: 'span 2' }}>
                            <strong>Complaint:</strong><br />
                            {job.complaint}
                        </div>
                    </div>
                </div>
            )}

            {activeTab === 'transition' && (
                <JobCardStateTransition 
                    jobId={jobId} 
                    currentState={job.state}
                    onTransition={(updatedJob) => setJob(updatedJob)}
                />
            )}

            {activeTab === 'estimate' && (
                <EstimateForm 
                    jobId={jobId} 
                    onEstimateCreated={fetchJobDetails}
                />
            )}

            {activeTab === 'history' && (
                <div className="card">
                    <div className="card__title">State History</div>
                    {/* State transition history would be fetched from audit_logs */}
                    <p style={{ color: 'var(--text-muted)' }}>
                        State history will be displayed here from audit logs.
                    </p>
                </div>
            )}
        </div>
    );
}
```

### Step 2.3: Update App.jsx with Detail Route
```jsx
// Add to App.jsx routes
<Route path="/jobs/:jobId" element={<JobCardDetailPage />} />
```

### Step 2.4: Update Jobs List to Link to Detail
```jsx
// In JobsPage.jsx, make rows clickable
<tr 
    key={job.id} 
    style={{ cursor: 'pointer' }}
    onClick={() => navigate(`/app/jobs/${job.id}`)}
>
    {/* ... cells */}
</tr>
```

---

# FIX 3: Implement Estimate Creation UI

## Problem
Cannot add parts and labor estimates to job cards.

## Implementation Steps

### Step 3.1: Create Estimate Form Component
```jsx
// frontend/src/components/EstimateForm.jsx
import { useState } from 'react';
import { Plus, Trash2, Calculator } from 'lucide-react';

export default function EstimateForm({ jobId, onEstimateCreated }) {
    const [lines, setLines] = useState([
        { part_id: '', description: '', quantity: 1, price: '', tax_rate: 18 }
    ]);
    const [laborHours, setLaborHours] = useState(0);
    const [laborRate, setLaborRate] = useState(500);
    const [loading, setLoading] = useState(false);

    const addLine = () => {
        setLines([...lines, { part_id: '', description: '', quantity: 1, price: '', tax_rate: 18 }]);
    };

    const removeLine = (index) => {
        setLines(lines.filter((_, i) => i !== index));
    };

    const updateLine = (index, field, value) => {
        const newLines = [...lines];
        newLines[index][field] = value;
        setLines(newLines);
    };

    const calculateTotals = () => {
        const partsTotal = lines.reduce((sum, line) => {
            return sum + (Number(line.price) * Number(line.quantity));
        }, 0);
        
        const laborTotal = laborHours * laborRate;
        
        const taxTotal = lines.reduce((sum, line) => {
            const lineTotal = Number(line.price) * Number(line.quantity);
            return sum + (lineTotal * (line.tax_rate / 100));
        }, 0);
        
        return {
            partsTotal,
            laborTotal,
            taxTotal,
            grandTotal: partsTotal + laborTotal + taxTotal
        };
    };

    const handleSubmit = async () => {
        setLoading(true);
        try {
            const token = localStorage.getItem('eka_token');
            const estimateData = {
                lines: lines.map(line => ({
                    part_id: line.part_id ? Number(line.part_id) : null,
                    description: line.description,
                    quantity: Number(line.quantity),
                    price: Number(line.price),
                    tax_rate: line.tax_rate / 100
                })),
                labor_hours: laborHours,
                labor_rate: laborRate
            };

            const res = await fetch(`/api/v1/job-cards/${jobId}/estimate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(estimateData)
            });

            if (!res.ok) throw new Error('Failed to create estimate');
            
            onEstimateCreated();
        } catch (err) {
            alert('Error: ' + err.message);
        } finally {
            setLoading(false);
        }
    };

    const totals = calculateTotals();

    return (
        <div className="card">
            <div className="card__title">Create Estimate</div>
            
            {/* Parts Lines */}
            <div style={{ marginBottom: '24px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                    <strong>Parts</strong>
                    <button className="btn btn--ghost btn--sm" onClick={addLine}>
                        <Plus size={14} /> Add Part
                    </button>
                </div>
                
                {lines.map((line, index) => (
                    <div key={index} style={{ 
                        display: 'grid', 
                        gridTemplateColumns: '2fr 1fr 1fr 1fr 80px 40px',
                        gap: '8px',
                        marginBottom: '8px',
                        alignItems: 'center'
                    }}>
                        <input 
                            className="input" 
                            placeholder="Description"
                            value={line.description}
                            onChange={(e) => updateLine(index, 'description', e.target.value)}
                        />
                        <input 
                            className="input" 
                            type="number"
                            placeholder="Qty"
                            value={line.quantity}
                            onChange={(e) => updateLine(index, 'quantity', e.target.value)}
                        />
                        <input 
                            className="input" 
                            type="number"
                            placeholder="Price"
                            value={line.price}
                            onChange={(e) => updateLine(index, 'price', e.target.value)}
                        />
                        <select 
                            className="input"
                            value={line.tax_rate}
                            onChange={(e) => updateLine(index, 'tax_rate', Number(e.target.value))}
                        >
                            <option value={5}>5% GST</option>
                            <option value={12}>12% GST</option>
                            <option value={18}>18% GST</option>
                            <option value={28}>28% GST</option>
                        </select>
                        <div style={{ fontSize: '0.86rem', textAlign: 'right' }}>
                            ₹{(line.price * line.quantity).toLocaleString()}
                        </div>
                        <button 
                            className="btn btn--ghost btn--sm" 
                            onClick={() => removeLine(index)}
                            disabled={lines.length === 1}
                        >
                            <Trash2 size={14} color="var(--danger)" />
                        </button>
                    </div>
                ))}
            </div>
            
            {/* Labor */}
            <div style={{ marginBottom: '24px' }}>
                <strong>Labor</strong>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 2fr', gap: '12px', marginTop: '8px' }}>
                    <div>
                        <label>Hours</label>
                        <input 
                            className="input" 
                            type="number"
                            value={laborHours}
                            onChange={(e) => setLaborHours(Number(e.target.value))}
                        />
                    </div>
                    <div>
                        <label>Rate (₹/hr)</label>
                        <input 
                            className="input" 
                            type="number"
                            value={laborRate}
                            onChange={(e) => setLaborRate(Number(e.target.value))}
                        />
                    </div>
                    <div style={{ display: 'flex', alignItems: 'flex-end', paddingBottom: '8px' }}>
                        <strong>Subtotal: ₹{(laborHours * laborRate).toLocaleString()}</strong>
                    </div>
                </div>
            </div>
            
            {/* Totals */}
            <div style={{ 
                background: 'var(--bg-glass)', 
                padding: '16px', 
                borderRadius: '8px',
                marginBottom: '16px'
            }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span>Parts Subtotal:</span>
                    <span>₹{totals.partsTotal.toLocaleString()}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span>Labor Subtotal:</span>
                    <span>₹{totals.laborTotal.toLocaleString()}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span>GST:</span>
                    <span>₹{totals.taxTotal.toLocaleString()}</span>
                </div>
                <div style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    paddingTop: '8px',
                    borderTop: '1px solid var(--border-glass)',
                    fontSize: '1.1rem',
                    fontWeight: 600
                }}>
                    <span>Grand Total:</span>
                    <span style={{ color: 'var(--accent)' }}>₹{totals.grandTotal.toLocaleString()}</span>
                </div>
            </div>
            
            <button 
                className="btn btn--primary"
                onClick={handleSubmit}
                disabled={loading || lines.some(l => !l.description || !l.price)}
            >
                <Calculator size={18} />
                {loading ? 'Creating...' : 'Create Estimate'}
            </button>
        </div>
    );
}
```

---

# FIX 4: Connect Backend APIs (Remove Mock Data)

## Problem
Invoices, Approvals, Dashboard using mock data instead of real API calls.

## Implementation Steps

### Step 4.1: Update Invoices Page
```jsx
// frontend/src/pages/InvoicesPage.jsx
import { useState, useEffect } from 'react';
import { FileText, Plus, Search, Download, Eye, CheckCircle } from 'lucide-react';

export default function InvoicesPage() {
    const [invoices, setInvoices] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [filter, setFilter] = useState('');

    useEffect(() => {
        fetchInvoices();
    }, []);

    const fetchInvoices = async () => {
        try {
            const token = localStorage.getItem('eka_token');
            const res = await fetch('/api/v1/invoices', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (!res.ok) throw new Error('Failed to fetch');
            const data = await res.json();
            setInvoices(data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const generateInvoice = async (jobId) => {
        try {
            const token = localStorage.getItem('eka_token');
            const res = await fetch('/api/v1/invoices', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ job_id: jobId })
            });
            if (!res.ok) throw new Error('Failed to generate');
            fetchInvoices();
        } catch (err) {
            alert('Error: ' + err.message);
        }
    };

    const downloadInvoice = async (invoiceId) => {
        try {
            const token = localStorage.getItem('eka_token');
            const res = await fetch(`/api/v1/invoices/${invoiceId}/pdf`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (!res.ok) throw new Error('Failed to download');
            
            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `invoice-${invoiceId}.pdf`;
            a.click();
        } catch (err) {
            alert('Error: ' + err.message);
        }
    };

    const markAsPaid = async (invoiceId) => {
        try {
            const token = localStorage.getItem('eka_token');
            const res = await fetch(`/api/v1/invoices/${invoiceId}/pay`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (!res.ok) throw new Error('Failed to mark paid');
            fetchInvoices();
        } catch (err) {
            alert('Error: ' + err.message);
        }
    };

    // ... rest of component with real data
}
```

### Step 4.2: Create Invoice Backend Router (if missing)
```python
# app/modules/invoices/router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from . import schema, service
from app.core.dependencies import get_db, get_tenant_id
from app.core.security import require_permission

router = APIRouter(prefix="/invoices", tags=["Invoices"])

@router.get("", response_model=list[schema.InvoiceResponse])
async def list_invoices(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(require_permission("can_manage_invoices"))
):
    """List all invoices for tenant."""
    return await service.list_invoices(db, tenant_id)

@router.post("", response_model=schema.InvoiceResponse)
async def create_invoice(
    invoice: schema.InvoiceCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(require_permission("can_create_invoice"))
):
    """Generate invoice from job card."""
    return await service.create_invoice(db, invoice, tenant_id, current_user["sub"])

@router.get("/{invoice_id}/pdf")
async def download_invoice_pdf(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(require_permission("can_manage_invoices"))
):
    """Download invoice as PDF."""
    return await service.generate_pdf(db, invoice_id, tenant_id)

@router.post("/{invoice_id}/pay", response_model=schema.InvoiceResponse)
async def mark_invoice_paid(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(require_permission("can_manage_invoices"))
):
    """Mark invoice as paid."""
    return await service.mark_paid(db, invoice_id, tenant_id, current_user["sub"])
```

### Step 4.3: Update Dashboard with Real Data
```jsx
// frontend/src/pages/DashboardPage.jsx
import { useState, useEffect } from 'react';

export default function DashboardPage() {
    const [kpis, setKpis] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        try {
            const token = localStorage.getItem('eka_token');
            const res = await fetch('/api/v1/dashboards/workshop', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (!res.ok) throw new Error('Failed to fetch');
            const data = await res.json();
            setKpis(data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    // ... rest with real data
}
```

---

# DEPENDENCIES BETWEEN FIXES

```
FIX 1: Add variant field
    ↓ (used by)
FIX 3: MG Engine calculations

FIX 2: State transition UI
    ↓ (requires)
FIX 3: Estimate creation (for APPROVED state)
    ↓ (leads to)
FIX 4: Invoice generation (for INVOICED state)
```

**Recommended Order:** 1 → 2 → 3 → 4

---

# TESTING CHECKLIST

## After Fix 1 (Vehicle variant)
- [ ] Can create vehicle with variant
- [ ] Can view vehicle variant in list
- [ ] MG calculation accepts variant field
- [ ] Database migration runs successfully

## After Fix 2 (State transitions)
- [ ] Can view job card detail page
- [ ] Valid transitions shown for each state
- [ ] Invalid transitions blocked
- [ ] State change persists after refresh
- [ ] Audit log captures transitions

## After Fix 3 (Estimates)
- [ ] Can add multiple part lines
- [ ] GST calculated correctly
- [ ] Labor hours added to total
- [ ] Estimate linked to job card
- [ ] Cannot transition to REPAIR without approved estimate

## After Fix 4 (Backend integration)
- [ ] Invoices load from database
- [ ] Can generate invoice from READY job
- [ ] Can download PDF
- [ ] Can mark as paid
- [ ] Dashboard shows real KPIs

---

*This plan contains all technical specifications needed to implement P0 fixes.*
