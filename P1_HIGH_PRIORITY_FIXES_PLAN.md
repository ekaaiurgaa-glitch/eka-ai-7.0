# P1 High Priority Fixes Plan
## Implementation Guide for Feature-Complete EKA-AI

---

# FIX 1: Complete MG Deterministic Engine

## Problem
MG Engine missing wear matrix, city index, and warranty adjustment calculations.

## Current State
- Basic calculation structure exists
- Missing curated data tables
- Risk calculation oversimplified

## Implementation Steps

### Step 1.1: Create Wear & Tear Matrix Tables
```python
# app/modules/mg_engine/models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON
from app.db.base import Base

class WearMatrix(Base):
    """Curated replacement intervals and costs per vehicle model."""
    __tablename__ = "wear_matrix"
    
    id = Column(Integer, primary_key=True)
    make = Column(String, nullable=False)
    model = Column(String, nullable=False)
    variant = Column(String, nullable=True)
    year_from = Column(Integer, nullable=False)
    year_to = Column(Integer, nullable=False)
    
    # Service intervals in months/km
    general_service_interval_km = Column(Integer, default=5000)
    general_service_cost = Column(Float, default=1500)
    
    # Parts with replacement intervals
    parts = Column(JSON, default=[
        {
            "part_code": "BRK_PAD",
            "name": "Brake Pads",
            "replace_every_km": 20000,
            "cost": 2500,
            "warranty_covered": False
        },
        {
            "part_code": "ENG_OIL",
            "name": "Engine Oil",
            "replace_every_km": 10000,
            "cost": 450,
            "warranty_covered": True  # Usually covered in first few services
        },
        {
            "part_code": "OIL_FILTER",
            "name": "Oil Filter",
            "replace_every_km": 10000,
            "cost": 250,
            "warranty_covered": True
        },
        {
            "part_code": "AIR_FILTER",
            "name": "Air Filter",
            "replace_every_km": 15000,
            "cost": 600,
            "warranty_covered": False
        },
        {
            "part_code": "CLUTCH_PLATE",
            "name": "Clutch Plate",
            "replace_every_km": 60000,
            "cost": 8000,
            "warranty_covered": False
        },
        {
            "part_code": "BATTERY",
            "name": "Battery",
            "replace_every_km": 40000,
            "cost": 4500,
            "warranty_covered": True
        },
        {
            "part_code": "TYRES",
            "name": "Tyres (set of 4)",
            "replace_every_km": 50000,
            "cost": 14000,
            "warranty_covered": False
        }
    ])

class CityLaborIndex(Base):
    """Labor cost multipliers by city tier."""
    __tablename__ = "city_labor_index"
    
    id = Column(Integer, primary_key=True)
    city_name = Column(String, nullable=False, unique=True)
    tier = Column(String, nullable=False)  # tier1, tier2, tier3
    labor_multiplier = Column(Float, default=1.0)
    
    # Example data:
    # Mumbai, Delhi, Bangalore -> tier1 -> 1.20
    # Pune, Hyderabad, Chennai -> tier2 -> 1.10
    # Other cities -> tier3 -> 1.00
```

### Step 1.2: Create Alembic Migration
```bash
alembic revision -m "add_mg_calculation_tables"
```

```python
def upgrade():
    op.create_table(
        'wear_matrix',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('make', sa.String(), nullable=False),
        sa.Column('model', sa.String(), nullable=False),
        sa.Column('variant', sa.String(), nullable=True),
        sa.Column('year_from', sa.Integer(), nullable=False),
        sa.Column('year_to', sa.Integer(), nullable=False),
        sa.Column('general_service_interval_km', sa.Integer(), nullable=True),
        sa.Column('general_service_cost', sa.Float(), nullable=True),
        sa.Column('parts', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_wear_matrix_make_model', 'wear_matrix', ['make', 'model'])
    
    op.create_table(
        'city_labor_index',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('city_name', sa.String(), nullable=False),
        sa.Column('tier', sa.String(), nullable=False),
        sa.Column('labor_multiplier', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('city_name')
    )
```

### Step 1.3: Seed Wear Matrix Data
```python
# seed_mg_data.py
async def seed_wear_matrix():
    matrices = [
        WearMatrix(
            make="Maruti",
            model="Swift",
            variant="VXI",
            year_from=2018,
            year_to=2024,
            general_service_interval_km=5000,
            general_service_cost=1200,
            parts=[
                {"part_code": "BRK_PAD", "name": "Brake Pads", "replace_every_km": 20000, "cost": 2200, "warranty_covered": False},
                {"part_code": "ENG_OIL", "name": "Engine Oil", "replace_every_km": 10000, "cost": 350, "warranty_covered": True},
                # ... more parts
            ]
        ),
        WearMatrix(
            make="Tata",
            model="Nexon",
            variant="XZA+",
            year_from=2020,
            year_to=2024,
            general_service_interval_km=7500,
            general_service_cost=1800,
            parts=[
                {"part_code": "BRK_PAD", "name": "Brake Pads", "replace_every_km": 25000, "cost": 2800, "warranty_covered": False},
                {"part_code": "ENG_OIL", "name": "Engine Oil", "replace_every_km": 15000, "cost": 500, "warranty_covered": True},
                # ... more parts
            ]
        ),
        # Add more vehicle models...
    ]
    
    # City labor indices
    cities = [
        CityLaborIndex(city_name="Mumbai", tier="tier1", labor_multiplier=1.25),
        CityLaborIndex(city_name="Delhi", tier="tier1", labor_multiplier=1.20),
        CityLaborIndex(city_name="Bangalore", tier="tier1", labor_multiplier=1.22),
        CityLaborIndex(city_name="Pune", tier="tier2", labor_multiplier=1.12),
        CityLaborIndex(city_name="Hyderabad", tier="tier2", labor_multiplier=1.10),
        CityLaborIndex(city_name="Chennai", tier="tier2", labor_multiplier=1.15),
        CityLaborIndex(city_name="Jaipur", tier="tier3", labor_multiplier=1.00),
        CityLaborIndex(city_name="Lucknow", tier="tier3", labor_multiplier=0.95),
    ]
```

### Step 1.4: Update Deterministic Engine
```python
# app/modules/mg_engine/deterministic_engine.py
from typing import Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .models import WearMatrix, CityLaborIndex

class MGDeterministicEngine:
    """
    Pure mathematical engine for MG calculations.
    NO AI - only deterministic formulas.
    """
    
    async def calculate(
        self,
        db: AsyncSession,
        make: str,
        model: str,
        variant: str,
        year: int,
        fuel_type: str,
        city: str,
        monthly_km: int,
        warranty_status: str,
        usage_type: str
    ) -> Dict:
        """
        Calculate Annual Maintenance Guarantee.
        
        Formula:
        1. Get wear matrix for vehicle
        2. Calculate parts costs over 12 months
        3. Apply city labor multiplier
        4. Calculate risk multiplier
        5. Apply warranty adjustments
        6. Return annual and monthly amounts
        """
        
        # 1. Get wear matrix
        result = await db.execute(
            select(WearMatrix).where(
                WearMatrix.make == make,
                WearMatrix.model == model,
                WearMatrix.year_from <= year,
                WearMatrix.year_to >= year
            )
        )
        wear_data = result.scalar_one_or_none()
        
        if not wear_data:
            raise ValueError(f"No wear data found for {make} {model} {year}")
        
        # 2. Get city multiplier
        city_result = await db.execute(
            select(CityLaborIndex).where(CityLaborIndex.city_name == city)
        )
        city_data = city_result.scalar_one_or_none()
        city_multiplier = city_data.labor_multiplier if city_data else 1.0
        
        # 3. Calculate annual parts cost
        annual_parts = await self._calculate_parts_cost(
            wear_data.parts,
            monthly_km,
            warranty_status == "under_warranty"
        )
        
        # 4. Calculate annual labor cost
        annual_labor = await self._calculate_labor_cost(
            wear_data,
            monthly_km,
            city_multiplier
        )
        
        # 5. Calculate risk multiplier
        risk_multiplier = self._calculate_risk_multiplier(
            usage_type=usage_type,
            monthly_km=monthly_km,
            vehicle_age=2026 - year  # Current year - manufacture year
        )
        
        # 6. Apply warranty adjustment
        warranty_adjustment = self._calculate_warranty_adjustment(
            annual_parts,
            warranty_status == "under_warranty",
            wear_data.parts
        )
        
        # 7. Final calculations
        final_annual_cost = (annual_parts + annual_labor) * risk_multiplier - warranty_adjustment
        monthly_mg = final_annual_cost / 12
        
        # 8. Determine risk level
        risk_level = self._get_risk_level(risk_multiplier)
        
        return {
            "annual_parts": round(annual_parts, 2),
            "annual_labor": round(annual_labor, 2),
            "city_adj": round(city_multiplier, 2),
            "risk_adj": round(risk_multiplier, 2),
            "warranty_adj": round(warranty_adjustment, 2),
            "final_annual_cost": round(final_annual_cost, 2),
            "monthly_mg": round(monthly_mg, 2),
            "risk_level": risk_level,
            "risk_buffer_pct": round((risk_multiplier - 1) * 100, 1),
            "parts_breakdown": await self._get_parts_breakdown(
                wear_data.parts, monthly_km, warranty_status == "under_warranty"
            ),
            "notes": "Calculated using deterministic engine with curated wear matrices. AI cannot compute financial projections."
        }
    
    async def _calculate_parts_cost(
        self,
        parts: List[Dict],
        monthly_km: int,
        under_warranty: bool
    ) -> float:
        """Calculate annual parts replacement costs."""
        annual_km = monthly_km * 12
        total_cost = 0.0
        
        for part in parts:
            if under_warranty and part.get("warranty_covered", False):
                continue  # Skip warranty-covered parts
            
            replace_every = part["replace_every_km"]
            cost = part["cost"]
            
            # How many times will this part be replaced in a year?
            replacements_per_year = annual_km / replace_every
            annual_cost = replacements_per_year * cost
            total_cost += annual_cost
        
        return total_cost
    
    async def _calculate_labor_cost(
        self,
        wear_data: WearMatrix,
        monthly_km: int,
        city_multiplier: float
    ) -> float:
        """Calculate annual labor costs."""
        annual_km = monthly_km * 12
        service_interval = wear_data.general_service_interval_km
        service_cost = wear_data.general_service_cost
        
        # Number of services per year
        services_per_year = annual_km / service_interval
        
        # Base labor cost
        base_labor = services_per_year * service_cost
        
        # Apply city multiplier
        adjusted_labor = base_labor * city_multiplier
        
        return adjusted_labor
    
    def _calculate_risk_multiplier(
        self,
        usage_type: str,
        monthly_km: int,
        vehicle_age: int
    ) -> float:
        """
        Calculate risk-based multiplier.
        
        Commercial usage: +15-25%
        High mileage (>2000km/mo): +10%
        Older vehicles (>5 years): +10%
        """
        base_multiplier = 1.0
        
        # Usage type risk
        if usage_type == "commercial":
            base_multiplier += 0.20
        elif usage_type == "ride_sharing":
            base_multiplier += 0.25
        
        # Mileage risk
        if monthly_km > 2500:
            base_multiplier += 0.10
        elif monthly_km > 2000:
            base_multiplier += 0.05
        
        # Age risk
        if vehicle_age > 7:
            base_multiplier += 0.15
        elif vehicle_age > 5:
            base_multiplier += 0.10
        elif vehicle_age > 3:
            base_multiplier += 0.05
        
        # Cap at 1.50 (50% buffer) per BRD
        return min(base_multiplier, 1.50)
    
    def _calculate_warranty_adjustment(
        self,
        annual_parts_cost: float,
        under_warranty: bool,
        parts: List[Dict]
    ) -> float:
        """Calculate warranty discount."""
        if not under_warranty:
            return 0.0
        
        # Estimate 30% of parts cost is warranty-covered
        warranty_coverage_ratio = 0.30
        return annual_parts_cost * warranty_coverage_ratio
    
    def _get_risk_level(self, risk_multiplier: float) -> str:
        """Convert multiplier to risk level."""
        if risk_multiplier >= 1.30:
            return "high"
        elif risk_multiplier >= 1.15:
            return "medium"
        return "low"
    
    async def _get_parts_breakdown(
        self,
        parts: List[Dict],
        monthly_km: int,
        under_warranty: bool
    ) -> List[Dict]:
        """Get detailed breakdown of parts costs."""
        annual_km = monthly_km * 12
        breakdown = []
        
        for part in parts:
            if under_warranty and part.get("warranty_covered", False):
                continue
            
            replacements = annual_km / part["replace_every_km"]
            annual_cost = replacements * part["cost"]
            
            breakdown.append({
                "name": part["name"],
                "annual_cost": round(annual_cost, 2),
                "replacements_per_year": round(replacements, 1)
            })
        
        return breakdown
```

### Step 1.5: Update MG Page to Show Breakdown
```jsx
// Update MGPage.jsx result display
{result && (
    <div className="card">
        <div className="card__title">MG Calculation Result</div>
        
        {/* Monthly MG - Highlighted */}
        <div style={{ textAlign: 'center', margin: '24px 0' }}>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Monthly MG Fee</div>
            <div style={{ fontSize: '2.8rem', fontWeight: 800, color: 'var(--accent-hover)' }}>
                ₹{result.monthly_mg.toLocaleString('en-IN')}
            </div>
        </div>
        
        {/* Risk Badge */}
        <div style={{ textAlign: 'center', marginBottom: '20px' }}>
            <span className={`badge ${
                result.risk_level === 'high' ? 'badge--danger' : 
                result.risk_level === 'medium' ? 'badge--warning' : 'badge--success'
            }`}>
                Risk: {result.risk_level.toUpperCase()}
            </span>
            <span className="badge badge--accent">Buffer: {result.risk_buffer_pct}%</span>
        </div>
        
        {/* Multipliers */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '20px' }}>
            <div style={{ background: 'var(--bg-glass)', padding: '10px', borderRadius: 8 }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>City Multiplier</div>
                <div style={{ fontWeight: 600 }}>{result.city_adj}x</div>
            </div>
            <div style={{ background: 'var(--bg-glass)', padding: '10px', borderRadius: 8 }}>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Risk Multiplier</div>
                <div style={{ fontWeight: 600 }}>{result.risk_adj}x</div>
            </div>
        </div>
        
        {/* Parts Breakdown - NEW */}
        <div style={{ marginBottom: '20px' }}>
            <div className="card__title" style={{ fontSize: '0.9rem', marginBottom: '10px' }}>
                Parts Breakdown (Annual)
            </div>
            {result.parts_breakdown?.map((part, i) => (
                <div key={i} style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between',
                    padding: '6px 0',
                    borderBottom: i < result.parts_breakdown.length - 1 ? '1px solid var(--border-glass)' : 'none'
                }}>
                    <span style={{ fontSize: '0.82rem' }}>{part.name}</span>
                    <span style={{ fontSize: '0.82rem', fontWeight: 500 }}>
                        ₹{part.annual_cost.toLocaleString()} 
                        <span style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>
                            ({part.replacements_per_year}x/yr)
                        </span>
                    </span>
                </div>
            ))}
        </div>
        
        {/* Totals */}
        <div style={{ 
            background: 'var(--bg-glass)', 
            padding: '16px', 
            borderRadius: 10 
        }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span>Annual Parts:</span>
                <span>₹{result.annual_parts.toLocaleString()}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span>Annual Labor:</span>
                <span>₹{result.annual_labor.toLocaleString()}</span>
            </div>
            {result.warranty_adj > 0 && (
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', color: 'var(--success)' }}>
                    <span>Warranty Discount:</span>
                    <span>-₹{result.warranty_adj.toLocaleString()}</span>
                </div>
            )}
            <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                paddingTop: '12px',
                borderTop: '1px solid var(--border-glass)',
                fontWeight: 600,
                fontSize: '1.1rem'
            }}>
                <span>Final Annual Cost:</span>
                <span>₹{result.final_annual_cost.toLocaleString()}</span>
            </div>
        </div>
        
        {/* Save Proposal Button - NEW */}
        <button 
            className="btn btn--primary" 
            style={{ width: '100%', marginTop: '16px' }}
            onClick={() => saveProposal(result)}
        >
            Save Proposal
        </button>
    </div>
)}
```

---

# FIX 2: Implement Invoice Generation from Job Card

## Problem
No way to generate invoice from READY job cards.

## Implementation Steps

### Step 2.1: Create Invoice Backend Module
```python
# app/modules/invoices/model.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON, Enum as SAEnum
from app.db.base import Base, TenantMixin, TimestampMixin
import enum

class InvoiceStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    overdue = "overdue"
    cancelled = "cancelled"

class Invoice(Base, TenantMixin, TimestampMixin):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True)
    invoice_no = Column(String, unique=True, index=True)
    job_id = Column(Integer, ForeignKey("job_cards.id"), nullable=False)
    
    # Customer info
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=True)
    customer_email = Column(String, nullable=True)
    
    # Amounts
    subtotal = Column(Float, nullable=False)
    tax_amount = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    
    # Tax breakdown
    tax_breakdown = Column(JSON, default={
        "cgst_9": 0.0,
        "sgst_9": 0.0,
        "igst_18": 0.0,
        "total_gst": 0.0
    })
    
    # Status
    status = Column(SAEnum(InvoiceStatus), default=InvoiceStatus.pending)
    
    # Payment
    paid_at = Column(DateTime, nullable=True)
    payment_method = Column(String, nullable=True)
    payment_reference = Column(String, nullable=True)

class InvoiceLine(Base, TenantMixin):
    """Individual line items on invoice."""
    __tablename__ = "invoice_lines"
    
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    
    # Line item details
    description = Column(String, nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=False)
    tax_rate = Column(Float, default=0.18)
    tax_amount = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    
    # Link to part if applicable
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=True)
```

### Step 2.2: Create Invoice Service
```python
# app/modules/invoices/service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from . import model, schema
from app.modules.job_cards import model as job_model

class InvoiceService:
    async def generate_from_job(
        self,
        db: AsyncSession,
        job_id: int,
        tenant_id: str,
        created_by: str
    ) -> model.Invoice:
        """Generate invoice from approved estimate on job card."""
        
        # 1. Get job card with estimate
        result = await db.execute(
            select(job_model.JobCard)
            .where(
                job_model.JobCard.id == job_id,
                job_model.JobCard.tenant_id == tenant_id,
                job_model.JobCard.state == "READY"
            )
        )
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(status_code=400, detail="Job card not found or not in READY state")
        
        # 2. Get approved estimate
        estimate_result = await db.execute(
            select(job_model.Estimate)
            .where(
                job_model.Estimate.job_id == job_id,
                job_model.Estimate.approved == True
            )
            .order_by(job_model.Estimate.created_at.desc())
        )
        estimate = estimate_result.scalar_one_or_none()
        
        if not estimate:
            raise HTTPException(status_code=400, detail="No approved estimate found for this job")
        
        # 3. Get vehicle/customer info
        vehicle_result = await db.execute(
            select(job_model.Vehicle).where(job_model.Vehicle.id == job.vehicle_id)
        )
        vehicle = vehicle_result.scalar_one_or_none()
        
        # 4. Calculate totals with GST
        subtotal = estimate.total_parts + estimate.total_labor
        
        # Determine tax type (intra-state vs inter-state)
        # For simplicity, assuming intra-state (CGST + SGST)
        gst_amount = subtotal * 0.18
        cgst = gst_amount / 2
        sgst = gst_amount / 2
        total = subtotal + gst_amount
        
        # 5. Generate invoice number
        invoice_no = await self._generate_invoice_number(db, tenant_id)
        
        # 6. Create invoice
        invoice = model.Invoice(
            invoice_no=invoice_no,
            job_id=job_id,
            customer_name=vehicle.owner_name if vehicle else "Unknown",
            subtotal=subtotal,
            tax_amount=gst_amount,
            total=total,
            tax_breakdown={
                "cgst_9": round(cgst, 2),
                "sgst_9": round(sgst, 2),
                "igst_18": 0.0,
                "total_gst": round(gst_amount, 2)
            },
            status=model.InvoiceStatus.pending,
            tenant_id=tenant_id
        )
        
        db.add(invoice)
        
        # 7. Create invoice lines from estimate
        for line in estimate.lines:
            invoice_line = model.InvoiceLine(
                invoice_id=invoice.id,
                description=line.get("description", "Service"),
                quantity=line.get("quantity", 1),
                unit_price=line.get("price", 0),
                tax_rate=line.get("tax_rate", 0.18),
                tax_amount=line.get("price", 0) * line.get("quantity", 1) * line.get("tax_rate", 0.18),
                total=line.get("price", 0) * line.get("quantity", 1) * (1 + line.get("tax_rate", 0.18)),
                part_id=line.get("part_id"),
                tenant_id=tenant_id
            )
            db.add(invoice_line)
        
        # 8. Update job state to INVOICED
        job.state = "INVOICED"
        
        await db.commit()
        await db.refresh(invoice)
        
        return invoice
    
    async def _generate_invoice_number(self, db: AsyncSession, tenant_id: str) -> str:
        """Generate unique invoice number: INV-{tenant}-{sequence}"""
        # Get count of invoices for tenant
        result = await db.execute(
            select(model.Invoice).where(model.Invoice.tenant_id == tenant_id)
        )
        count = len(result.scalars().all())
        return f"INV-{tenant_id[:4].upper()}-{count + 1:04d}"
    
    async def mark_paid(
        self,
        db: AsyncSession,
        invoice_id: int,
        tenant_id: str,
        payment_method: str = "cash",
        payment_reference: str = None
    ) -> model.Invoice:
        """Mark invoice as paid."""
        
        result = await db.execute(
            select(model.Invoice).where(
                model.Invoice.id == invoice_id,
                model.Invoice.tenant_id == tenant_id
            )
        )
        invoice = result.scalar_one_or_none()
        
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        if invoice.status != model.InvoiceStatus.pending:
            raise HTTPException(status_code=400, detail="Invoice is not in pending status")
        
        from datetime import datetime
        invoice.status = model.InvoiceStatus.paid
        invoice.paid_at = datetime.utcnow()
        invoice.payment_method = payment_method
        invoice.payment_reference = payment_reference
        
        # Update job state to PAID
        job_result = await db.execute(
            select(job_model.JobCard).where(job_model.JobCard.id == invoice.job_id)
        )
        job = job_result.scalar_one()
        job.state = "PAID"
        
        await db.commit()
        await db.refresh(invoice)
        
        return invoice
```

### Step 2.3: Add "Generate Invoice" Button to Job Detail
```jsx
// In JobCardDetailPage.jsx
{job.state === 'READY' && (
    <div className="card" style={{ marginTop: '20px' }}>
        <div className="card__title">Invoice</div>
        <p style={{ color: 'var(--text-muted)', marginBottom: '16px' }}>
            This job is ready for billing. Generate an invoice to proceed.
        </p>
        <button 
            className="btn btn--primary"
            onClick={async () => {
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
                    const invoice = await res.json();
                    alert(`Invoice ${invoice.invoice_no} generated successfully!`);
                    fetchJobDetails(); // Refresh
                } catch (err) {
                    alert('Error: ' + err.message);
                }
            }}
        >
            <FileText size={18} />
            Generate Invoice
        </button>
    </div>
)}
```

---

# FIX 3: Implement Intent Parser for Operator AI

## Problem
Operator AI requires manual form fill instead of natural language input.

## Implementation

### Step 3.1: Create NLU Intent Parser
```python
# app/modules/operator/intent_parser.py
import re
from typing import Dict, Optional
from pydantic import BaseModel

class ParsedIntent(BaseModel):
    intent: str  # create_job_card, generate_invoice, etc.
    confidence: float
    entities: Dict[str, str]
    missing_entities: list[str]

class IntentParser:
    """
    Rule-based + LLM hybrid intent parser.
    Uses regex patterns for common queries, falls back to LLM for complex ones.
    """
    
    # Intent patterns
    PATTERNS = {
        "create_job_card": [
            r"(?:create|open|start)\s+(?:a\s+)?(?:new\s+)?job\s+(?:card)?\s+(?:for\s+)?(?P<vehicle>\w+)",
            r"job\s+(?:card)?\s+(?:for\s+)?(?P<vehicle>\w+)\s+(?:with\s+)?(?P<complaint>.+)",
            r"(?P<vehicle>\w+)\s+(?:needs|has)\s+(?P<complaint>.+)"
        ],
        "generate_invoice": [
            r"(?:generate|create)\s+(?:an?\s+)?invoice\s+(?:for\s+)?(?:job\s+)?(?P<job_id>\w+)",
            r"bill\s+(?:for\s+)?(?:job\s+)?(?P<job_id>\w+)"
        ],
        "query_status": [
            r"(?:what's|what is)\s+(?:the\s+)?status\s+(?:of\s+)?(?:job\s+)?(?P<job_id>\w+)",
            r"(?:check|show)\s+(?:job\s+)?(?P<job_id>\w+)"
        ]
    }
    
    REQUIRED_ENTITIES = {
        "create_job_card": ["vehicle", "complaint"],
        "generate_invoice": ["job_id"],
        "query_status": ["job_id"]
    }
    
    def parse(self, query: str) -> ParsedIntent:
        """Parse natural language query into structured intent."""
        query_lower = query.lower().strip()
        
        # Try regex patterns first
        for intent, patterns in self.PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, query_lower, re.IGNORECASE)
                if match:
                    entities = match.groupdict()
                    missing = [
                        field for field in self.REQUIRED_ENTITIES.get(intent, [])
                        if field not in entities or not entities[field]
                    ]
                    
                    return ParsedIntent(
                        intent=intent,
                        confidence=0.85 if not missing else 0.60,
                        entities=entities,
                        missing_entities=missing
                    )
        
        # Fallback: LLM-based parsing (would call Gemini here)
        return self._llm_fallback_parse(query)
    
    def _llm_fallback_parse(self, query: str) -> ParsedIntent:
        """Use LLM for complex queries not matching patterns."""
        # This would make an API call to Gemini with a structured prompt
        # For now, return unknown intent
        return ParsedIntent(
            intent="unknown",
            confidence=0.0,
            entities={},
            missing_entities=[]
        )

# Usage in Operator router
# intent = parser.parse("Create job card for MH12AB1234 with brake issue")
# Returns: intent=intent.create_job_card, entities={"vehicle": "MH12AB1234", "complaint": "brake issue"}
```

### Step 3.2: Add Natural Language Input to Operator Page
```jsx
// Add to OperatorPage.jsx
const [naturalInput, setNaturalInput] = useState('');
const [parsedIntent, setParsedIntent] = useState(null);

const parseIntent = async () => {
    const res = await fetch('/api/v1/operator/parse', {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ query: naturalInput })
    });
    const data = await res.json();
    setParsedIntent(data);
    
    // Auto-fill form based on parsed intent
    if (data.intent === 'create_job_card') {
        setFormData({
            vehicle_number: data.entities.vehicle || '',
            complaint: data.entities.complaint || ''
        });
    }
};

// JSX
<div className="card" style={{ marginBottom: '20px' }}>
    <div className="card__title">Natural Language Input</div>
    <div style={{ display: 'flex', gap: '10px' }}>
        <input 
            className="input" 
            placeholder="e.g., Create job card for MH12AB1234 with brake issue"
            value={naturalInput}
            onChange={(e) => setNaturalInput(e.target.value)}
            style={{ flex: 1 }}
        />
        <button className="btn btn--primary" onClick={parseIntent}>
            Parse
        </button>
    </div>
    
    {parsedIntent && (
        <div style={{ marginTop: '16px', padding: '12px', background: 'var(--bg-glass)', borderRadius: 8 }}>
            <div><strong>Detected Intent:</strong> {parsedIntent.intent}</div>
            <div><strong>Confidence:</strong> {(parsedIntent.confidence * 100).toFixed(0)}%</div>
            {parsedIntent.missing_entities.length > 0 && (
                <div style={{ color: 'var(--warning)', marginTop: '8px' }}>
                    Missing: {parsedIntent.missing_entities.join(', ')}
                </div>
            )}
        </div>
    )}
</div>
```

---

# FIX 4: Add Approval Rules Engine

## Problem
Approval workflow exists but no rules engine to determine which transitions require approval.

## Implementation

### Step 4.1: Create Approval Rules Configuration
```python
# app/modules/approvals/rules.py
from enum import Enum
from typing import List, Dict
from pydantic import BaseModel

class ApprovalTrigger(str, Enum):
    ESTIMATE_EXCEEDS_AMOUNT = "estimate_exceeds_amount"
    STATE_TRANSITION = "state_transition"
    DISCOUNT_APPLIED = "discount_applied"
    LATE_JOB = "late_job"

class ApprovalRule(BaseModel):
    trigger: ApprovalTrigger
    condition: Dict  # e.g., {"amount_threshold": 10000}
    approver_roles: List[str]  # e.g., ["owner", "manager"]
    description: str

# Default approval rules per BRD
DEFAULT_APPROVAL_RULES = [
    ApprovalRule(
        trigger=ApprovalTrigger.ESTIMATE_EXCEEDS_AMOUNT,
        condition={"amount_threshold": 10000},
        approver_roles=["owner"],
        description="Estimates over ₹10,000 require owner approval"
    ),
    ApprovalRule(
        trigger=ApprovalTrigger.STATE_TRANSITION,
        condition={"from_state": "ESTIMATE_PENDING", "to_state": "APPROVAL_PENDING"},
        approver_roles=["manager", "owner"],
        description="All estimates require approval before repair"
    ),
    ApprovalRule(
        trigger=ApprovalTrigger.DISCOUNT_APPLIED,
        condition={"discount_pct_threshold": 10},
        approver_roles=["owner"],
        description="Discounts over 10% require owner approval"
    ),
    ApprovalRule(
        trigger=ApprovalTrigger.LATE_JOB,
        condition={"days_overdue": 7},
        approver_roles=["manager"],
        description="Jobs overdue by 7+ days require manager review"
    )
]

class ApprovalRulesEngine:
    def check_approval_required(
        self,
        trigger: ApprovalTrigger,
        context: Dict
    ) -> tuple[bool, List[str]]:
        """
        Check if approval is required and return required roles.
        
        Returns: (approval_required, required_roles)
        """
        for rule in DEFAULT_APPROVAL_RULES:
            if rule.trigger != trigger:
                continue
            
            if self._evaluate_condition(rule.condition, context):
                return True, rule.approver_roles
        
        return False, []
    
    def _evaluate_condition(self, condition: Dict, context: Dict) -> bool:
        """Evaluate if condition matches context."""
        for key, expected_value in condition.items():
            actual_value = context.get(key)
            
            if key.endswith("_threshold"):
                # Numeric comparison
                if actual_value is None or actual_value < expected_value:
                    return False
            elif key.startswith("from_") or key.startswith("to_"):
                # State matching
                if actual_value != expected_value:
                    return False
            else:
                # Exact match
                if actual_value != expected_value:
                    return False
        
        return True
```

### Step 4.2: Integrate Rules into Job Card Service
```python
# In job_card/service.py
from app.modules.approvals.rules import ApprovalRulesEngine, ApprovalTrigger

async def transition_job_card_state(
    self,
    db: AsyncSession,
    job_id: int,
    new_state: str,
    tenant_id: str,
    user_id: str
):
    """Transition with approval check."""
    
    # ... existing validation ...
    
    # Check if approval required
    rules_engine = ApprovalRulesEngine()
    approval_required, required_roles = rules_engine.check_approval_required(
        trigger=ApprovalTrigger.STATE_TRANSITION,
        context={
            "from_state": job.state,
            "to_state": new_state,
            "estimate_amount": estimate.total if estimate else 0
        }
    )
    
    if approval_required:
        # Create approval request instead of transitioning
        await self._create_approval_request(
            db, job_id, job.state, new_state, required_roles, tenant_id
        )
        raise HTTPException(
            status_code=202,  # Accepted but pending
            detail=f"Transition requires approval from: {', '.join(required_roles)}"
        )
    
    # Proceed with transition
    job.state = new_state
    await db.commit()
    return job
```

---

# FIX 5: Add Vehicle Service History

## Problem
Cannot view complete service history for a vehicle.

## Implementation

### Step 5.1: Create Service History API
```python
# app/modules/vehicles/service.py
async def get_vehicle_service_history(
    self,
    db: AsyncSession,
    vehicle_id: int,
    tenant_id: str
) -> Dict:
    """Get complete service history for a vehicle."""
    
    from app.modules.job_cards import model as job_model
    from app.modules.invoices import model as invoice_model
    
    # Get all job cards for vehicle
    result = await db.execute(
        select(job_model.JobCard)
        .where(
            job_model.JobCard.vehicle_id == vehicle_id,
            job_model.JobCard.tenant_id == tenant_id
        )
        .order_by(job_model.JobCard.created_at.desc())
    )
    jobs = result.scalars().all()
    
    history = []
    for job in jobs:
        # Get invoice if exists
        invoice_result = await db.execute(
            select(invoice_model.Invoice)
            .where(invoice_model.Invoice.job_id == job.id)
        )
        invoice = invoice_result.scalar_one_or_none()
        
        history.append({
            "job_id": job.id,
            "job_no": job.job_no,
            "date": job.created_at,
            "complaint": job.complaint,
            "state": job.state,
            "total_cost": invoice.total if invoice else None,
            "invoice_no": invoice.invoice_no if invoice else None
        })
    
    return {
        "vehicle_id": vehicle_id,
        "total_visits": len(history),
        "total_spent": sum(h["total_cost"] for h in history if h["total_cost"]),
        "history": history
    }
```

### Step 5.2: Add Service History UI
```jsx
// VehicleDetailPage.jsx
const [serviceHistory, setServiceHistory] = useState([]);

useEffect(() => {
    fetchServiceHistory();
}, []);

const fetchServiceHistory = async () => {
    const res = await fetch(`/api/v1/vehicles/${vehicleId}/history`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await res.json();
    setServiceHistory(data.history);
};

// In JSX
<div className="card">
    <div className="card__title">Service History ({serviceHistory.length} visits)</div>
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {serviceHistory.map((visit) => (
            <div key={visit.job_id} style={{ 
                padding: '12px', 
                background: 'var(--bg-glass)', 
                borderRadius: 8 
            }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <strong>{visit.job_no}</strong>
                    <span style={{ color: 'var(--text-muted)' }}>
                        {new Date(visit.date).toLocaleDateString()}
                    </span>
                </div>
                <div style={{ marginTop: '4px' }}>{visit.complaint}</div>
                <div style={{ marginTop: '8px', display: 'flex', gap: '16px' }}>
                    <span className={`badge badge--${visit.state === 'CLOSED' ? 'success' : 'info'}`}>
                        {visit.state}
                    </span>
                    {visit.total_cost && (
                        <span>₹{visit.total_cost.toLocaleString()}</span>
                    )}
                </div>
            </div>
        ))}
    </div>
</div>
```

---

# FIX 6: Add RAG Reference Display to Chat

## Problem
Chat responses don't show which knowledge documents were referenced.

## Implementation

### Step 6.1: Update Chat Response Schema
```python
# app/modules/chat/schema.py
class ChatQueryResponse(BaseModel):
    issue_summary: str
    probable_causes: list[str]
    diagnostic_steps: list[str]
    safety_advisory: str
    confidence_level: float
    rag_references: Optional[list[dict]] = None  # NEW FIELD
    tokens_used: Optional[int] = None
```

### Step 6.2: Update Chat Page UI
```jsx
// In ChatPage.jsx, after displaying response
{data.rag_references && data.rag_references.length > 0 && (
    <div style={{ 
        marginTop: '12px', 
        padding: '8px 12px', 
        background: 'var(--bg-glass)', 
        borderRadius: 6,
        fontSize: '0.78rem'
    }}>
        <div style={{ color: 'var(--text-muted)', marginBottom: '4px' }}>
            <BookOpen size={12} style={{ display: 'inline', marginRight: 4 }} />
            Sources:
        </div>
        {data.rag_references.map((ref, i) => (
            <div key={i} style={{ color: 'var(--accent)', marginLeft: '16px' }}>
                • {ref.title} (relevance: {(ref.score * 100).toFixed(0)}%)
            </div>
        ))}
    </div>
)}
```

---

# TESTING CHECKLIST

## After Fix 1 (MG Engine)
- [ ] Wear matrix returns correct parts for vehicle model
- [ ] City multiplier applied correctly
- [ ] Warranty adjustment reduces cost appropriately
- [ ] Parts breakdown shows individual component costs
- [ ] Risk multiplier capped at 1.50

## After Fix 2 (Invoice Generation)
- [ ] Invoice generated only from READY jobs
- [ ] GST calculated correctly (CGST/SGST split)
- [ ] Invoice number format correct
- [ ] Job state changes to INVOICED
- [ ] Payment marks job as PAID

## After Fix 3 (Intent Parser)
- [ ] Common phrases parsed correctly
- [ ] Missing entities identified
- [ ] Confidence score shown
- [ ] Form auto-fills from parsed intent

## After Fix 4 (Approval Rules)
- [ ] Large estimates trigger approval
- [ ] Correct approver roles assigned
- [ ] Approval request created correctly
- [ ] Notification sent to approvers

## After Fix 5 (Service History)
- [ ] All jobs for vehicle listed
- [ ] Costs aggregated correctly
- [ ] Chronological order maintained
- [ ] Click to view job detail

## After Fix 6 (RAG References)
- [ ] Sources displayed below response
- [ ] Relevance scores shown
- [ ] Clickable to view document
- [ ] Collapsible section

---

*P1 fixes add significant value but don't block basic functionality.*
