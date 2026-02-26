import { Download, CheckCircle, Clock } from 'lucide-react';

export default function InvoiceView({ invoice, onMarkPaid }) {
    if (!invoice) return <div style={{ padding: 20, color: 'var(--text-muted)' }}>No invoice generated yet.</div>;

    const isPaid = (invoice.status || 'UNPAID') === 'PAID';

    return (
        <div className="card invoice-container" style={{ padding: '32px', background: 'white', color: '#1a1a1a' }}>
            {/* Invoice Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '40px' }}>
                <div>
                    <h1 style={{ margin: 0, color: 'var(--accent)', fontSize: '2rem' }}>INVOICE</h1>
                    <div style={{ marginTop: 8, color: '#666' }}>#{invoice.id}</div>
                </div>
                <div style={{ textAlign: 'right' }}>
                    <div style={{ fontWeight: 700, fontSize: '1.2rem' }}>EKA Workshop Solutions</div>
                    <div style={{ fontSize: '0.85rem', color: '#666' }}>123 Tech Park, Hinjewadi</div>
                    <div style={{ fontSize: '0.85rem', color: '#666' }}>Pune, MH - 411057</div>
                    <div style={{ fontSize: '0.85rem', color: '#666' }}>GSTIN: 27AAAAA0000A1Z5</div>
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 40, marginBottom: '40px' }}>
                <div>
                    <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#999', textTransform: 'uppercase', marginBottom: 8 }}>Billed To</div>
                    <div style={{ fontWeight: 600 }}>Customer Name</div>
                    <div style={{ fontSize: '0.85rem', color: '#666' }}>Vehicle: TN 01 AB 1234</div>
                    <div style={{ fontSize: '0.85rem', color: '#666' }}>Job Ref: {invoice.job_id}</div>
                </div>
                <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#999', textTransform: 'uppercase', marginBottom: 8 }}>Invoice Details</div>
                    <div style={{ fontSize: '0.85rem', color: '#666' }}>Date: {new Date(invoice.created_at).toLocaleDateString()}</div>
                    <div style={{ marginTop: 8 }}>
                        <span className={`badge ${isPaid ? 'badge--success' : 'badge--warning'}`} style={{ color: 'white' }}>
                            {invoice.status || 'UNPAID'}
                        </span>
                    </div>
                </div>
            </div>

            {/* Table */}
            <table style={{ width: '100%', borderCollapse: 'collapse', marginBottom: '32px' }}>
                <thead>
                    <tr style={{ borderBottom: '2px solid #eee' }}>
                        <th style={{ textAlign: 'left', padding: '12px 8px', fontSize: '0.8rem', color: '#999' }}>DESCRIPTION</th>
                        <th style={{ textAlign: 'center', padding: '12px 8px', fontSize: '0.8rem', color: '#999' }}>QTY</th>
                        <th style={{ textAlign: 'right', padding: '12px 8px', fontSize: '0.8rem', color: '#999' }}>PRICE</th>
                        <th style={{ textAlign: 'right', padding: '12px 8px', fontSize: '0.8rem', color: '#999' }}>GST</th>
                        <th style={{ textAlign: 'right', padding: '12px 8px', fontSize: '0.8rem', color: '#999' }}>TOTAL</th>
                    </tr>
                </thead>
                <tbody>
                    {invoice.lines.map((line, i) => (
                        <tr key={i} style={{ borderBottom: '1px solid #f9f9f9' }}>
                            <td style={{ padding: '16px 8px', fontWeight: 500 }}>{line.description}</td>
                            <td style={{ padding: '16px 8px', textAlign: 'center' }}>{line.quantity}</td>
                            <td style={{ padding: '16px 8px', textAlign: 'right' }}>₹{line.price.toLocaleString('en-IN')}</td>
                            <td style={{ padding: '16px 8px', textAlign: 'right' }}>
                                ₹{(line.gst_details?.cgst + line.gst_details?.sgst + line.gst_details?.igst || 0).toLocaleString('en-IN')}
                            </td>
                            <td style={{ padding: '16px 8px', textAlign: 'right', fontWeight: 600 }}>₹{line.gst_details?.total.toLocaleString('en-IN')}</td>
                        </tr>
                    ))}
                </tbody>
            </table>

            {/* Totals Section */}
            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                <div style={{ width: '300px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
                        <span style={{ color: '#666' }}>Taxable Value</span>
                        <span>₹{(invoice.total_amount - invoice.tax_amount).toLocaleString('en-IN')}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
                        <span style={{ color: '#666' }}>Total GST</span>
                        <span>₹{invoice.tax_amount.toLocaleString('en-IN')}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', paddingTop: 16, borderTop: '2px solid #eee', fontWeight: 800, fontSize: '1.2rem' }}>
                        <span>GRAND TOTAL</span>
                        <span style={{ color: 'var(--accent)' }}>₹{invoice.total_amount.toLocaleString('en-IN')}</span>
                    </div>
                </div>
            </div>

            {/* Actions (Hidden during print) */}
            <div className="no-print" style={{ marginTop: '40px', display: 'flex', gap: 12, borderTop: '1px solid #eee', paddingTop: 24 }}>
                <button className="btn btn--primary" onClick={() => window.print()}>
                    <Download size={18} /> Print / Save PDF
                </button>
                {!isPaid && (
                    <button className="btn btn--ghost" onClick={() => onMarkPaid(invoice.id)}>
                        <CheckCircle size={18} /> Mark as Paid
                    </button>
                )}
            </div>

            <style dangerouslySetInnerHTML={{
                __html: `
                @media print {
                    .no-print { display: none !important; }
                    body * { visibility: hidden; }
                    .invoice-container, .invoice-container * { visibility: visible; }
                    .invoice-container { position: absolute; left: 0; top: 0; width: 100%; border: none !important; box-shadow: none !important; }
                }
            `}} />
        </div>
    );
}
