# P2 Medium Priority Fixes Plan
## Enhancement Guide for Improved UX and Convenience

---

# FIX 1: PDF Invoice Download

## Problem
Invoice download button is non-functional.

## Implementation

### Step 1.1: Install PDF Generation Library
```bash
pip install reportlab jinja2 weasyprint
```

### Step 1.2: Create PDF Generator Service
```python
# app/modules/invoices/pdf_generator.py
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
from typing import Dict

class InvoicePDFGenerator:
    """Generate professional PDF invoices."""
    
    def generate(self, invoice: Dict) -> BytesIO:
        """Generate PDF from invoice data."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch)
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#6366f1'),
            spaceAfter=30
        )
        
        # Header
        elements.append(Paragraph("EKA-AI Workshop", title_style))
        elements.append(Paragraph("GSTIN: 29ABCDE1234F1Z5", styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Invoice Info
        elements.append(Paragraph(f"<b>Invoice:</b> {invoice['invoice_no']}", styles['Heading3']))
        elements.append(Paragraph(f"<b>Date:</b> {invoice['created_at']}", styles['Normal']))
        elements.append(Paragraph(f"<b>Status:</b> {invoice['status'].upper()}", styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Customer Info
        elements.append(Paragraph("<b>Bill To:</b>", styles['Heading4']))
        elements.append(Paragraph(invoice['customer_name'], styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Line Items Table
        table_data = [['Description', 'Qty', 'Rate', 'Tax', 'Amount']]
        for line in invoice.get('lines', []):
            table_data.append([
                line['description'],
                str(line['quantity']),
                f"₹{line['unit_price']:,.2f}",
                f"₹{line['tax_amount']:,.2f}",
                f"₹{line['total']:,.2f}"
            ])
        
        # Totals
        table_data.append(['', '', '', '<b>Subtotal:</b>', f"₹{invoice['subtotal']:,.2f}"])
        table_data.append(['', '', '', '<b>GST (18%):</b>', f"₹{invoice['tax_amount']:,.2f}"])
        table_data.append(['', '', '', '<b>Total:</b>', f"₹{invoice['total']:,.2f}"])
        
        table = Table(table_data, colWidths=[3*inch, 0.5*inch, 1*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -4), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (3, -3), (4, -1), 'Helvetica-Bold'),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.5*inch))
        
        # Footer
        elements.append(Paragraph("Thank you for your business!", styles['Normal']))
        elements.append(Paragraph("For queries, contact: support@eka-ai.in", styles['Normal']))
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
```

### Step 1.3: Add PDF Endpoint
```python
# app/modules/invoices/router.py
from fastapi.responses import StreamingResponse

@router.get("/{invoice_id}/pdf")
async def download_invoice_pdf(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(require_permission("can_manage_invoices"))
):
    """Download invoice as PDF."""
    invoice = await service.get_invoice(db, invoice_id, tenant_id)
    
    from .pdf_generator import InvoicePDFGenerator
    generator = InvoicePDFGenerator()
    pdf_buffer = generator.generate(invoice)
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=invoice-{invoice['invoice_no']}.pdf"
        }
    )
```

### Step 1.4: Frontend Integration
```jsx
// Already exists in InvoicesPage, just needs backend connection
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
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    } catch (err) {
        alert('Error downloading PDF: ' + err.message);
    }
};
```

---

# FIX 2: Dashboard Trend Charts

## Problem
Dashboard shows only current values, no historical trends.

## Implementation

### Step 2.1: Install Chart Library
```bash
npm install recharts
```

### Step 2.2: Create Revenue Chart Component
```jsx
// frontend/src/components/charts/RevenueChart.jsx
import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

export default function RevenueChart({ data }) {
    return (
        <div style={{ width: '100%', height: 300 }}>
            <ResponsiveContainer>
                <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border-glass)" />
                    <XAxis 
                        dataKey="month" 
                        stroke="var(--text-muted)"
                        fontSize={12}
                    />
                    <YAxis 
                        stroke="var(--text-muted)"
                        fontSize={12}
                        tickFormatter={(value) => `₹${(value/1000).toFixed(0)}K`}
                    />
                    <Tooltip 
                        contentStyle={{ 
                            backgroundColor: 'var(--bg-secondary)', 
                            border: '1px solid var(--border-glass)',
                            borderRadius: 8
                        }}
                        formatter={(value) => [`₹${value.toLocaleString()}`, 'Revenue']}
                    />
                    <Legend />
                    <Line 
                        type="monotone" 
                        dataKey="revenue" 
                        stroke="var(--accent)" 
                        strokeWidth={2}
                        dot={{ fill: 'var(--accent)' }}
                        activeDot={{ r: 8 }}
                    />
                    <Line 
                        type="monotone" 
                        dataKey="target" 
                        stroke="var(--success)" 
                        strokeDasharray="5 5"
                        strokeWidth={2}
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
}
```

### Step 2.3: Create Job State Distribution Chart
```jsx
// frontend/src/components/charts/JobStateChart.jsx
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const COLORS = {
    'OPEN': '#3b82f6',
    'DIAGNOSIS': '#6366f1',
    'REPAIR': '#8b5cf6',
    'QC_PDI': '#ec4899',
    'READY': '#14b8a6',
    'INVOICED': '#0ea5e9',
    'CLOSED': '#22c55e'
};

export default function JobStateChart({ data }) {
    const chartData = Object.entries(data).map(([state, count]) => ({
        name: state,
        value: count,
        color: COLORS[state] || '#64748b'
    }));
    
    return (
        <div style={{ width: '100%', height: 300 }}>
            <ResponsiveContainer>
                <PieChart>
                    <Pie
                        data={chartData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={100}
                        fill="#8884d8"
                        paddingAngle={5}
                        dataKey="value"
                        label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    >
                        {chartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                    </Pie>
                    <Tooltip 
                        contentStyle={{ 
                            backgroundColor: 'var(--bg-secondary)', 
                            border: '1px solid var(--border-glass)',
                            borderRadius: 8
                        }}
                    />
                    <Legend />
                </PieChart>
            </ResponsiveContainer>
        </div>
    );
}
```

### Step 2.4: Add to Dashboard
```jsx
// frontend/src/pages/DashboardPage.jsx
import RevenueChart from '../components/charts/RevenueChart';
import JobStateChart from '../components/charts/JobStateChart';

// Mock data - in production would come from API
const revenueData = [
    { month: 'Jan', revenue: 420000, target: 400000 },
    { month: 'Feb', revenue: 380000, target: 400000 },
    { month: 'Mar', revenue: 510000, target: 450000 },
    { month: 'Apr', revenue: 470000, target: 450000 },
    { month: 'May', revenue: 540000, target: 500000 },
    { month: 'Jun', revenue: 487500, target: 500000 },
];

const jobStateData = {
    'OPEN': 8,
    'DIAGNOSIS': 5,
    'REPAIR': 14,
    'QC_PDI': 5,
    'READY': 3,
    'CLOSED': 123
};

// In JSX
<div className="grid grid--2" style={{ marginBottom: 24 }}>
    <div className="card">
        <div className="card__title">Revenue Trend (6 months)</div>
        <RevenueChart data={revenueData} />
    </div>
    <div className="card">
        <div className="card__title">Job Distribution</div>
        <JobStateChart data={jobStateData} />
    </div>
</div>
```

### Step 2.5: Backend API for Historical Data
```python
# app/modules/dashboard/service.py
async def get_revenue_trend(
    self,
    db: AsyncSession,
    tenant_id: str,
    months: int = 6
) -> List[Dict]:
    """Get monthly revenue for trend chart."""
    from sqlalchemy import func, extract
    from datetime import datetime, timedelta
    from app.modules.invoices import model as invoice_model
    
    start_date = datetime.utcnow() - timedelta(days=30*months)
    
    result = await db.execute(
        select(
            extract('month', invoice_model.Invoice.created_at).label('month'),
            extract('year', invoice_model.Invoice.created_at).label('year'),
            func.sum(invoice_model.Invoice.total).label('revenue')
        )
        .where(
            invoice_model.Invoice.tenant_id == tenant_id,
            invoice_model.Invoice.created_at >= start_date,
            invoice_model.Invoice.status == "paid"
        )
        .group_by('year', 'month')
        .order_by('year', 'month')
    )
    
    return [
        {
            "month": f"{row.year}-{row.month:02d}",
            "revenue": float(row.revenue or 0),
            "target": 500000  # Could come from tenant settings
        }
        for row in result.all()
    ]
```

---

# FIX 3: Email/SMS Notifications

## Problem
No notifications sent for approvals, job status changes, or overdue invoices.

## Implementation

### Step 3.1: Install Notification Library
```bash
pip install sendgrid twilio
```

### Step 3.2: Create Notification Service
```python
# app/core/notifications.py
from typing import List, Optional
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.rest import Client

class NotificationService:
    def __init__(self):
        self.sendgrid = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        self.twilio = Client(os.getenv('TWILIO_SID'), os.getenv('TWILIO_TOKEN'))
        self.from_email = "notifications@eka-ai.in"
        self.from_phone = "+1234567890"
    
    async def send_approval_request(
        self,
        to_email: str,
        approver_name: str,
        requester_name: str,
        job_no: str,
        approval_url: str
    ):
        """Send approval request email."""
        message = Mail(
            from_email=self.from_email,
            to_emails=to_email,
            subject=f"Approval Required: Job {job_no}",
            html_content=f"""
            <h2>Approval Request</h2>
            <p>Hello {approver_name},</p>
            <p>{requester_name} has requested approval for job <strong>{job_no}</strong>.</p>
            <p><a href="{approval_url}" style="padding: 10px 20px; background: #6366f1; color: white; text-decoration: none; border-radius: 5px;">Review & Approve</a></p>
            <p>This request will expire in 24 hours.</p>
            """
        )
        await self.sendgrid.send(message)
    
    async def send_job_status_update(
        self,
        to_phone: str,
        customer_name: str,
        job_no: str,
        new_status: str
    ):
        """Send SMS for job status update."""
        message = f"Hi {customer_name}, your vehicle (Job: {job_no}) status has been updated to: {new_status}. Track at: https://eka-ai.in/track/{job_no}"
        
        await self.twilio.messages.create(
            body=message,
            from_=self.from_phone,
            to=to_phone
        )
    
    async def send_invoice_reminder(
        self,
        to_email: str,
        customer_name: str,
        invoice_no: str,
        amount: float,
        due_date: str
    ):
        """Send invoice due reminder."""
        message = Mail(
            from_email=self.from_email,
            to_emails=to_email,
            subject=f"Invoice #{invoice_no} Due",
            html_content=f"""
            <h2>Payment Reminder</h2>
            <p>Hello {customer_name},</p>
            <p>This is a reminder that invoice <strong>#{invoice_no}</strong> for <strong>₹{amount:,.2f}</strong> is due on {due_date}.</p>
            <p>Please make the payment to avoid late fees.</p>
            <p><a href="https://eka-ai.in/pay/{invoice_no}" style="padding: 10px 20px; background: #22c55e; color: white; text-decoration: none; border-radius: 5px;">Pay Now</a></p>
            """
        )
        await self.sendgrid.send(message)
```

### Step 3.3: Integrate Notifications
```python
# In job_cards/service.py when state changes
async def transition_job_card_state(...):
    # ... existing transition logic ...
    
    # Send notification
    from app.core.notifications import NotificationService
    notification_service = NotificationService()
    
    if new_state == "READY":
        # Notify customer vehicle is ready
        await notification_service.send_job_status_update(
            to_phone=customer.phone,
            customer_name=customer.name,
            job_no=job.job_no,
            new_status="READY for pickup"
        )
    
    elif new_state == "REPAIR":
        # Notify customer work has started
        await notification_service.send_job_status_update(...)
```

---

# FIX 4: Vehicle Search & Filter

## Problem
Cannot search or filter vehicles in the list.

## Implementation

### Step 4.1: Update Vehicles Page with Search
```jsx
// frontend/src/pages/VehiclesPage.jsx
const [searchTerm, setSearchTerm] = useState('');
const [filterFuel, setFilterFuel] = useState('');

const filteredVehicles = MOCK_VEHICLES.filter(v => {
    const matchesSearch = 
        v.plate_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
        v.make.toLowerCase().includes(searchTerm.toLowerCase()) ||
        v.model.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesFuel = !filterFuel || v.fuel_type === filterFuel;
    
    return matchesSearch && matchesFuel;
});

// In JSX - Add above vehicle grid
<div style={{ display: 'flex', gap: 12, marginBottom: 20 }}>
    <div style={{ flex: 1, position: 'relative' }}>
        <Search size={16} style={{ 
            position: 'absolute', 
            left: 12, 
            top: '50%', 
            transform: 'translateY(-50%)', 
            color: 'var(--text-muted)' 
        }} />
        <input 
            className="input" 
            style={{ paddingLeft: 36 }}
            placeholder="Search by plate, make, or model..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
        />
    </div>
    <select 
        className="input" 
        style={{ width: 150 }}
        value={filterFuel}
        onChange={(e) => setFilterFuel(e.target.value)}
    >
        <option value="">All Fuel Types</option>
        <option value="petrol">Petrol</option>
        <option value="diesel">Diesel</option>
        <option value="electric">Electric</option>
        <option value="hybrid">Hybrid</option>
    </select>
</div>

// Use filteredVehicles instead of MOCK_VEHICLES
<div className="grid grid--3">
    {filteredVehicles.map(v => (...))}
</div>
```

### Step 4.2: Backend Search API
```python
# app/modules/vehicles/router.py
@router.get("/search")
async def search_vehicles(
    q: str = Query(None, description="Search query"),
    fuel_type: str = Query(None),
    make: str = Query(None),
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(get_current_user)
):
    """Search vehicles by plate, make, model."""
    from sqlalchemy import or_
    
    query = select(model.Vehicle).where(model.Vehicle.tenant_id == tenant_id)
    
    if q:
        search_filter = f"%{q}%"
        query = query.where(
            or_(
                model.Vehicle.plate_number.ilike(search_filter),
                model.Vehicle.make.ilike(search_filter),
                model.Vehicle.model.ilike(search_filter)
            )
        )
    
    if fuel_type:
        query = query.where(model.Vehicle.fuel_type == fuel_type)
    
    if make:
        query = query.where(model.Vehicle.make.ilike(f"%{make}%"))
    
    result = await db.execute(query.limit(20))
    return result.scalars().all()
```

---

# FIX 5: Dark/Light Theme Toggle

## Problem
Application only supports dark theme.

## Implementation

### Step 5.1: Create Theme Context
```jsx
// frontend/src/context/ThemeContext.jsx
import { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export function ThemeProvider({ children }) {
    const [theme, setTheme] = useState(() => {
        return localStorage.getItem('theme') || 'dark';
    });
    
    useEffect(() => {
        localStorage.setItem('theme', theme);
        document.documentElement.setAttribute('data-theme', theme);
    }, [theme]);
    
    const toggleTheme = () => {
        setTheme(prev => prev === 'dark' ? 'light' : 'dark');
    };
    
    return (
        <ThemeContext.Provider value={{ theme, toggleTheme }}>
            {children}
        </ThemeContext.Provider>
    );
}

export const useTheme = () => useContext(ThemeContext);
```

### Step 5.2: Update CSS for Theme Variables
```css
/* frontend/src/index.css */
:root {
  /* Dark theme (default) */
  --bg-primary: #0a0e17;
  --bg-secondary: #111827;
  --bg-glass: rgba(255, 255, 255, 0.05);
  --text-primary: #f9fafb;
  --text-secondary: #9ca3af;
  --text-muted: #6b7280;
  --accent: #6366f1;
  --accent-hover: #818cf8;
  --border-glass: rgba(255, 255, 255, 0.1);
}

[data-theme="light"] {
  --bg-primary: #ffffff;
  --bg-secondary: #f3f4f6;
  --bg-glass: rgba(0, 0, 0, 0.05);
  --text-primary: #111827;
  --text-secondary: #4b5563;
  --text-muted: #9ca3af;
  --accent: #4f46e5;
  --accent-hover: #4338ca;
  --border-glass: rgba(0, 0, 0, 0.1);
}
```

### Step 5.3: Add Theme Toggle Button
```jsx
// In Sidebar.jsx or Header
import { Moon, Sun } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

function ThemeToggle() {
    const { theme, toggleTheme } = useTheme();
    
    return (
        <button 
            className="btn btn--ghost btn--sm"
            onClick={toggleTheme}
            title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
        >
            {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>
    );
}
```

---

# FIX 6: Keyboard Shortcuts

## Problem
No keyboard shortcuts for power users.

## Implementation

### Step 6.1: Create Shortcuts Hook
```jsx
// frontend/src/hooks/useKeyboardShortcuts.js
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export function useKeyboardShortcuts() {
    const navigate = useNavigate();
    
    useEffect(() => {
        const handleKeyDown = (e) => {
            // Ignore if typing in input
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                return;
            }
            
            switch(e.key) {
                case 'j':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        navigate('/app/jobs');
                    }
                    break;
                case 'v':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        navigate('/app/vehicles');
                    }
                    break;
                case 'c':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        navigate('/app/chat');
                    }
                    break;
                case 'd':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        navigate('/app');
                    }
                    break;
                case 'n':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        // Trigger new job modal if on jobs page
                        // This would need context
                    }
                    break;
                case '?':
                    e.preventDefault();
                    // Show shortcuts help modal
                    break;
                case 'Escape':
                    // Close modals
                    break;
            }
        };
        
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [navigate]);
}

// Usage in AppLayout
useKeyboardShortcuts();
```

### Step 6.2: Create Shortcuts Help Modal
```jsx
// frontend/src/components/ShortcutsHelpModal.jsx
const SHORTCUTS = [
    { key: 'Ctrl + D', description: 'Go to Dashboard' },
    { key: 'Ctrl + J', description: 'Go to Job Cards' },
    { key: 'Ctrl + V', description: 'Go to Vehicles' },
    { key: 'Ctrl + C', description: 'Go to Chat' },
    { key: 'Ctrl + N', description: 'New Job Card' },
    { key: '?', description: 'Show this help' },
    { key: 'Escape', description: 'Close modal' },
];

export default function ShortcutsHelpModal({ isOpen, onClose }) {
    if (!isOpen) return null;
    
    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal" onClick={e => e.stopPropagation()}>
                <h3>Keyboard Shortcuts</h3>
                <div style={{ display: 'grid', gap: '8px', marginTop: '16px' }}>
                    {SHORTCUTS.map((shortcut) => (
                        <div key={shortcut.key} style={{ 
                            display: 'flex', 
                            justifyContent: 'space-between',
                            padding: '8px 0',
                            borderBottom: '1px solid var(--border-glass)'
                        }}>
                            <kbd style={{ 
                                background: 'var(--bg-glass)', 
                                padding: '4px 8px', 
                                borderRadius: 4,
                                fontFamily: 'monospace'
                            }}>
                                {shortcut.key}
                            </kbd>
                            <span>{shortcut.description}</span>
                        </div>
                    ))}
                </div>
                <button className="btn btn--primary" onClick={onClose} style={{ marginTop: '16px' }}>
                    Close
                </button>
            </div>
        </div>
    );
}
```

---

# FIX 7: Data Export (CSV/Excel)

## Problem
Cannot export data for external analysis.

## Implementation

### Step 7.1: Install Export Library
```bash
pip install openpyxl
npm install papaparse
```

### Step 7.2: Create Export Service
```python
# app/core/export_service.py
import csv
import io
from openpyxl import Workbook
from typing import List, Dict

class ExportService:
    def to_csv(self, data: List[Dict], filename: str) -> io.BytesIO:
        """Export data to CSV."""
        output = io.StringIO()
        if data:
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        
        buffer = io.BytesIO()
        buffer.write(output.getvalue().encode('utf-8'))
        buffer.seek(0)
        return buffer
    
    def to_excel(self, data: List[Dict], sheet_name: str = "Data") -> io.BytesIO:
        """Export data to Excel."""
        wb = Workbook()
        ws = wb.active
        ws.title = sheet_name
        
        if data:
            # Headers
            headers = list(data[0].keys())
            ws.append(headers)
            
            # Data rows
            for row in data:
                ws.append([row.get(h) for h in headers])
            
            # Auto-adjust column widths
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width
        
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer
```

### Step 7.3: Add Export Endpoints
```python
# app/modules/job_cards/router.py
from fastapi.responses import StreamingResponse
from app.core.export_service import ExportService

@router.get("/export/csv")
async def export_jobs_csv(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(require_permission("can_export_data"))
):
    """Export job cards to CSV."""
    jobs = await service.list_job_cards(db, tenant_id)
    
    export_service = ExportService()
    csv_buffer = export_service.to_csv(
        [{"Job No": j.job_no, "State": j.state, "Complaint": j.complaint} for j in jobs],
        "job_cards"
    )
    
    return StreamingResponse(
        csv_buffer,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=job_cards.csv"}
    )

@router.get("/export/excel")
async def export_jobs_excel(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(require_permission("can_export_data"))
):
    """Export job cards to Excel."""
    jobs = await service.list_job_cards(db, tenant_id)
    
    export_service = ExportService()
    excel_buffer = export_service.to_excel(
        [{"Job No": j.job_no, "State": j.state, "Complaint": j.complaint} for j in jobs],
        "Job Cards"
    )
    
    return StreamingResponse(
        excel_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=job_cards.xlsx"}
    )
```

### Step 7.4: Frontend Export Buttons
```jsx
// In JobsPage.jsx
<div style={{ display: 'flex', gap: 8 }}>
    <button 
        className="btn btn--ghost btn--sm"
        onClick={() => window.open('/api/v1/job-cards/export/csv', '_blank')}
    >
        <Download size={14} /> CSV
    </button>
    <button 
        className="btn btn--ghost btn--sm"
        onClick={() => window.open('/api/v1/job-cards/export/excel', '_blank')}
    >
        <Download size={14} /> Excel
    </button>
</div>
```

---

# TESTING CHECKLIST

## After Fix 1 (PDF)
- [ ] PDF generated with correct layout
- [ ] GST split shown correctly
- [ ] Company branding included
- [ ] Download works on all browsers

## After Fix 2 (Charts)
- [ ] Revenue trend line displays
- [ ] Job distribution pie chart shows
- [ ] Hover tooltips work
- [ ] Responsive on mobile

## After Fix 3 (Notifications)
- [ ] Approval request emails sent
- [ ] SMS delivered for status updates
- [ ] Invoice reminders sent
- [ ] Unsubscribe link works

## After Fix 4 (Search)
- [ ] Search by plate number works
- [ ] Search by make/model works
- [ ] Fuel type filter works
- [ ] Results update in real-time

## After Fix 5 (Theme)
- [ ] Toggle switches theme
- [ ] Preference saved
- [ ] All components themed
- [ ] No flash on page load

## After Fix 6 (Shortcuts)
- [ ] All shortcuts work
- [ ] Help modal displays
- [ ] Shortcuts disabled in inputs
- [ ] Mac Cmd key works

## After Fix 7 (Export)
- [ ] CSV downloads correctly
- [ ] Excel opens without errors
- [ ] All columns included
- [ ] UTF-8 characters preserved

---

*P2 fixes are convenience features that enhance user experience but aren't required for core functionality.*
