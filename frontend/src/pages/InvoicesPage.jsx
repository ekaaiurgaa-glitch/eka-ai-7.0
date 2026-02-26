import { useState, useEffect } from 'react';
import { FileText, Plus, Search, Download, Eye, CheckCircle } from 'lucide-react';

export default function InvoicesPage() {
    const [invoices, setInvoices] = useState([]);
    const [search, setSearch] = useState('');
    const [filter, setFilter] = useState('');
    const [selectedInvoice, setSelectedInvoice] = useState(null);
    const [showCreate, setShowCreate] = useState(false);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        fetchInvoices();
    }, []);

    const fetchInvoices = async () => {
        try {
            setLoading(true);
            const token = localStorage.getItem('eka_token');
            const res = await fetch('/api/v1/invoices', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (!res.ok) throw new Error('Failed to fetch invoices');
            const data = await res.json();
            setInvoices(data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateInvoice = async (e) => {
        e.preventDefault();
        setSubmitting(true);
        try {
            const formData = new FormData(e.target);
            const jobId = formData.get('jobId');

            const token = localStorage.getItem('eka_token');
            const res = await fetch('/api/v1/invoices', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    job_id: parseInt(jobId),
                    lines: [
                        { description: "General Service", quantity: 1, price: 5000, tax_rate: 18.0 }
                    ]
                }),
            });
            if (!res.ok) throw new Error('Failed to generate invoice');

            setShowCreate(false);
            fetchInvoices();
        } catch (err) {
            alert(err.message);
        } finally {
            setSubmitting(false);
        }
    };

    const handleMarkPaid = async (invoiceId) => {
        try {
            const token = localStorage.getItem('eka_token');
            const res = await fetch(`/api/v1/invoices/${invoiceId}/pay`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (!res.ok) throw new Error('Failed to mark as paid');

            setSelectedInvoice(null);
            fetchInvoices();
        } catch (err) {
            alert(err.message);
        }
    };

    const filtered = invoices.filter(inv => {
        const status = inv.status?.toLowerCase() || 'pending';
        if (filter && status !== filter) return false;
        if (search && !inv.id.toString().includes(search) &&
            !(inv.customer_name || '').toLowerCase().includes(search.toLowerCase())) return false;
        return true;
    });

    if (loading && invoices.length === 0) return <div style={{ padding: 20, color: 'var(--text-muted)' }}>Loading invoices...</div>;

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
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 12, marginTop: 12 }}>
                            <div>
                                <label>Job Card ID (Internal ID)</label>
                                <input className="input" name="jobId" placeholder="e.g., 1" required />
                            </div>
                        </div>
                        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 8 }}>
                            Note: This currently uses default lines for demo. Real invoice will pull from Job Card Estimate.
                        </p>
                        <div style={{ display: 'flex', gap: 8, marginTop: 14 }}>
                            <button className="btn btn--primary btn--sm" type="submit" disabled={submitting}>
                                {submitting ? 'Generating...' : 'Generate'}
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
                    <div className="card__title">Invoice Details - #{selectedInvoice.id}</div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 20, marginTop: 16 }}>
                        <div>
                            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: 4 }}>Job Reference</div>
                            <div style={{ fontWeight: 600 }}>#{selectedInvoice.job_id}</div>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: 4 }}>Total Amount</div>
                            <div style={{ fontSize: '1.8rem', fontWeight: 700, color: 'var(--accent-hover)' }}>
                                ₹{selectedInvoice.total_amount.toLocaleString('en-IN')}
                            </div>
                            <span className={`badge ${(selectedInvoice.status || 'PENDING').toLowerCase() === 'paid' ? 'badge--success' : 'badge--warning'}`} style={{ marginTop: 8 }}>
                                {selectedInvoice.status || 'PENDING'}
                            </span>
                        </div>
                    </div>
                    <div style={{ marginTop: 20, padding: '16px', background: 'var(--bg-glass)', borderRadius: 10 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                            <span style={{ color: 'var(--text-secondary)' }}>Taxable Value</span>
                            <span>₹{(selectedInvoice.total_amount - selectedInvoice.tax_amount).toLocaleString('en-IN')}</span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                            <span style={{ color: 'var(--text-secondary)' }}>GST</span>
                            <span>₹{selectedInvoice.tax_amount.toLocaleString('en-IN')}</span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', paddingTop: 12, borderTop: '1px solid var(--border-glass)', fontWeight: 600 }}>
                            <span>Total (Inc. Tax)</span>
                            <span>₹{selectedInvoice.total_amount.toLocaleString('en-IN')}</span>
                        </div>
                    </div>
                    <div style={{ display: 'flex', gap: 10, marginTop: 16 }}>
                        <button className="btn btn--primary btn--sm" disabled>
                            <Download size={14} style={{ marginRight: 6 }} /> Download PDF (P2)
                        </button>
                        {selectedInvoice.status !== 'PAID' && (
                            <button className="btn btn--ghost btn--sm" onClick={() => handleMarkPaid(selectedInvoice.id)}>
                                <CheckCircle size={14} style={{ marginRight: 6 }} /> Mark as Paid
                            </button>
                        )}
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
                </select>
            </div>

            {/* Summary Cards */}
            <div className="grid grid--3" style={{ marginBottom: 24 }}>
                {[
                    { label: 'Total Invoiced', value: `₹${invoices.reduce((a, b) => a + b.total_amount, 0).toLocaleString('en-IN')}`, color: 'var(--accent)' },
                    { label: 'Paid', value: `₹${invoices.filter(i => (i.status || 'PENDING').toLowerCase() === 'paid').reduce((a, b) => a + b.total_amount, 0).toLocaleString('en-IN')}`, color: 'var(--success)' },
                    { label: 'Unpaid', value: `₹${invoices.filter(i => (i.status || 'PENDING').toLowerCase() !== 'paid').reduce((a, b) => a + b.total_amount, 0).toLocaleString('en-IN')}`, color: 'var(--warning)' },
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
                            <th>ID</th>
                            <th>Job Ref</th>
                            <th>Amount</th>
                            <th>Status</th>
                            <th>Created</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filtered.length === 0 ? (
                            <tr><td colSpan="6" style={{ textAlign: 'center', color: 'var(--text-muted)', padding: 20 }}>No invoices found</td></tr>
                        ) : filtered.map(inv => {
                            const isPaid = (inv.status || 'PENDING').toLowerCase() === 'paid';
                            return (
                                <tr key={inv.id} style={{ cursor: 'pointer' }} onClick={() => setSelectedInvoice(inv)}>
                                    <td style={{ fontWeight: 600, color: 'var(--accent-hover)' }}>#{inv.id}</td>
                                    <td>#{inv.job_id}</td>
                                    <td style={{ fontWeight: 600 }}>₹{inv.total_amount.toLocaleString('en-IN')}</td>
                                    <td>
                                        <span className={`badge ${isPaid ? 'badge--success' : 'badge--warning'}`}>
                                            {inv.status || 'PENDING'}
                                        </span>
                                    </td>
                                    <td>{new Date(inv.created_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}</td>
                                    <td>
                                        <button
                                            className="btn btn--ghost btn--sm"
                                            onClick={(e) => { e.stopPropagation(); setSelectedInvoice(inv); }}
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
