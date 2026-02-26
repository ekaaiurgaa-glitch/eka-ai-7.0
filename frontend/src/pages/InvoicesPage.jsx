import { useState, useEffect } from 'react';
import { FileText, Plus, Search, Download, Eye, CheckCircle } from 'lucide-react';
import { api } from '../api';

const MOCK_INVOICES = [
    { id: 1, invoice_no: 'INV-0023', job_no: 'JC-0044', customer: 'Rahul Sharma', amount: 12400, gst_amount: 2232, total: 14632, status: 'paid', created_at: '2026-02-25T10:30:00' },
    { id: 2, invoice_no: 'INV-0022', job_no: 'JC-0042', customer: 'Priya Patel', amount: 8500, gst_amount: 1530, total: 10030, status: 'pending', created_at: '2026-02-24T16:00:00' },
    { id: 3, invoice_no: 'INV-0021', job_no: 'JC-0041', customer: 'Amit Kumar', amount: 15200, gst_amount: 2736, total: 17936, status: 'overdue', created_at: '2026-02-22T11:00:00' },
    { id: 4, invoice_no: 'INV-0020', job_no: 'JC-0040', customer: 'Sneha Reddy', amount: 5600, gst_amount: 1008, total: 6608, status: 'paid', created_at: '2026-02-20T14:00:00' },
];

const statusConfig = {
    paid: { badge: 'badge--success', label: 'Paid' },
    pending: { badge: 'badge--warning', label: 'Pending' },
    overdue: { badge: 'badge--danger', label: 'Overdue' },
};

export default function InvoicesPage() {
    const [invoices, setInvoices] = useState(MOCK_INVOICES);
    const [search, setSearch] = useState('');
    const [filter, setFilter] = useState('');
    const [selectedInvoice, setSelectedInvoice] = useState(null);
    const [showCreate, setShowCreate] = useState(false);
    const [loading, setLoading] = useState(false);

    const filtered = invoices.filter(inv => {
        if (filter && inv.status !== filter) return false;
        if (search && !inv.invoice_no.toLowerCase().includes(search.toLowerCase()) && 
            !inv.customer.toLowerCase().includes(search.toLowerCase())) return false;
        return true;
    });

    const handleCreateInvoice = async (e) => {
        e.preventDefault();
        setLoading(true);
        // API call would go here
        setTimeout(() => {
            setShowCreate(false);
            setLoading(false);
        }, 1000);
    };

    return (
        <div className="fade-in">
            <div className="main__header">
                <h2 style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <FileText size={22} color="var(--accent)" /> Invoices
                </h2>
                <button className="btn btn--primary" onClick={() => setShowCreate(!showCreate)}>
                    <Plus size={18} /> Generate Invoice
                </button>
            </div>

            {/* Create Form */}
            {showCreate && (
                <div className="card" style={{ marginBottom: 20 }}>
                    <div className="card__title">Generate New Invoice</div>
                    <form onSubmit={handleCreateInvoice}>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, marginTop: 12 }}>
                            <div>
                                <label>Job Card ID</label>
                                <input className="input" placeholder="e.g., JC-0044" required />
                            </div>
                            <div>
                                <label>Customer Name</label>
                                <input className="input" placeholder="Customer name" required />
                            </div>
                            <div>
                                <label>Payment Terms</label>
                                <select className="input">
                                    <option value="immediate">Immediate</option>
                                    <option value="net15">Net 15 Days</option>
                                    <option value="net30">Net 30 Days</option>
                                </select>
                            </div>
                        </div>
                        <div style={{ display: 'flex', gap: 8, marginTop: 14 }}>
                            <button className="btn btn--primary btn--sm" type="submit" disabled={loading}>
                                {loading ? 'Generating...' : 'Generate'}
                            </button>
                            <button className="btn btn--ghost btn--sm" type="button" onClick={() => setShowCreate(false)}>Cancel</button>
                        </div>
                    </form>
                </div>
            )}

            {/* Invoice Detail Modal */}
            {selectedInvoice && (
                <div className="card" style={{ marginBottom: 20, position: 'relative' }}>
                    <button 
                        onClick={() => setSelectedInvoice(null)}
                        style={{ position: 'absolute', top: 12, right: 12, background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
                    >
                        ✕
                    </button>
                    <div className="card__title">Invoice Details - {selectedInvoice.invoice_no}</div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 20, marginTop: 16 }}>
                        <div>
                            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: 4 }}>Customer</div>
                            <div style={{ fontWeight: 600 }}>{selectedInvoice.customer}</div>
                            <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: 4 }}>Job: {selectedInvoice.job_no}</div>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: 4 }}>Total Amount</div>
                            <div style={{ fontSize: '1.8rem', fontWeight: 700, color: 'var(--accent-hover)' }}>
                                ₹{selectedInvoice.total.toLocaleString('en-IN')}
                            </div>
                            <span className={`badge ${statusConfig[selectedInvoice.status].badge}`} style={{ marginTop: 8 }}>
                                {statusConfig[selectedInvoice.status].label}
                            </span>
                        </div>
                    </div>
                    <div style={{ marginTop: 20, padding: '16px', background: 'var(--bg-glass)', borderRadius: 10 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                            <span style={{ color: 'var(--text-secondary)' }}>Subtotal</span>
                            <span>₹{selectedInvoice.amount.toLocaleString('en-IN')}</span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                            <span style={{ color: 'var(--text-secondary)' }}>GST (18%)</span>
                            <span>₹{selectedInvoice.gst_amount.toLocaleString('en-IN')}</span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', paddingTop: 12, borderTop: '1px solid var(--border-glass)', fontWeight: 600 }}>
                            <span>Total</span>
                            <span>₹{selectedInvoice.total.toLocaleString('en-IN')}</span>
                        </div>
                    </div>
                    <div style={{ display: 'flex', gap: 10, marginTop: 16 }}>
                        <button className="btn btn--primary btn--sm">
                            <Download size={14} style={{ marginRight: 6 }} /> Download PDF
                        </button>
                        <button className="btn btn--ghost btn--sm">
                            <CheckCircle size={14} style={{ marginRight: 6 }} /> Mark as Paid
                        </button>
                    </div>
                </div>
            )}

            {/* Filters */}
            <div style={{ display: 'flex', gap: 12, marginBottom: 20 }}>
                <div style={{ flex: 1, position: 'relative' }}>
                    <Search size={16} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                    <input 
                        className="input" 
                        style={{ paddingLeft: 36 }} 
                        placeholder="Search invoices..." 
                        value={search} 
                        onChange={e => setSearch(e.target.value)} 
                    />
                </div>
                <select className="input" style={{ width: 160 }} value={filter} onChange={e => setFilter(e.target.value)}>
                    <option value="">All Status</option>
                    <option value="paid">Paid</option>
                    <option value="pending">Pending</option>
                    <option value="overdue">Overdue</option>
                </select>
            </div>

            {/* Summary Cards */}
            <div className="grid grid--4" style={{ marginBottom: 24 }}>
                {[
                    { label: 'Total Invoiced', value: `₹${invoices.reduce((a, b) => a + b.total, 0).toLocaleString('en-IN')}`, color: 'var(--accent)' },
                    { label: 'Paid', value: `₹${invoices.filter(i => i.status === 'paid').reduce((a, b) => a + b.total, 0).toLocaleString('en-IN')}`, color: 'var(--success)' },
                    { label: 'Pending', value: `₹${invoices.filter(i => i.status === 'pending').reduce((a, b) => a + b.total, 0).toLocaleString('en-IN')}`, color: 'var(--warning)' },
                    { label: 'Overdue', value: `₹${invoices.filter(i => i.status === 'overdue').reduce((a, b) => a + b.total, 0).toLocaleString('en-IN')}`, color: 'var(--danger)' },
                ].map((stat, i) => (
                    <div className="card" key={i}>
                        <div className="card__title" style={{ fontSize: '0.78rem' }}>{stat.label}</div>
                        <div style={{ fontSize: '1.3rem', fontWeight: 700, color: stat.color, marginTop: 4 }}>{stat.value}</div>
                    </div>
                ))}
            </div>

            {/* Table */}
            <div className="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>Invoice No</th>
                            <th>Job Ref</th>
                            <th>Customer</th>
                            <th>Amount</th>
                            <th>Status</th>
                            <th>Created</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filtered.map(inv => {
                            const cfg = statusConfig[inv.status];
                            return (
                                <tr key={inv.id} style={{ cursor: 'pointer' }}>
                                    <td style={{ fontWeight: 600, color: 'var(--accent-hover)' }}>{inv.invoice_no}</td>
                                    <td>{inv.job_no}</td>
                                    <td>{inv.customer}</td>
                                    <td style={{ fontWeight: 600 }}>₹{inv.total.toLocaleString('en-IN')}</td>
                                    <td>
                                        <span className={`badge ${cfg.badge}`}>
                                            {cfg.label}
                                        </span>
                                    </td>
                                    <td>{new Date(inv.created_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}</td>
                                    <td>
                                        <button 
                                            className="btn btn--ghost btn--sm" 
                                            onClick={() => setSelectedInvoice(inv)}
                                        >
                                            <Eye size={14} />
                                        </button>
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
