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
            return sum + (Number(line.price || 0) * Number(line.quantity || 0));
        }, 0);

        const laborTotal = Number(laborHours) * Number(laborRate);

        const taxTotal = lines.reduce((sum, line) => {
            const lineTotal = Number(line.price || 0) * Number(line.quantity || 0);
            return sum + (lineTotal * (Number(line.tax_rate) / 100));
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
                    tax_rate: Number(line.tax_rate) / 100
                })),
                labor_hours: Number(laborHours),
                labor_rate: Number(laborRate)
            };

            const res = await fetch(`/api/v1/job-cards/${jobId}/estimate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(estimateData)
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || 'Failed to create estimate');
            }

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
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px', alignItems: 'center' }}>
                    <h4 style={{ margin: 0 }}>Parts & Materials</h4>
                    <button className="btn btn--ghost btn--sm" onClick={addLine}>
                        <Plus size={14} /> Add Part
                    </button>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {lines.map((line, index) => (
                        <div key={index} style={{
                            display: 'grid',
                            gridTemplateColumns: '2fr 80px 100px 120px 100px 40px',
                            gap: '8px',
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
                                onChange={(e) => updateLine(index, 'tax_rate', e.target.value)}
                            >
                                <option value={5}>5% GST</option>
                                <option value={12}>12% GST</option>
                                <option value={18}>18% GST</option>
                                <option value={28}>28% GST</option>
                            </select>
                            <div style={{ fontSize: '0.86rem', textAlign: 'right', fontWeight: 600 }}>
                                ₹{((Number(line.price || 0) * Number(line.quantity || 0))).toLocaleString('en-IN')}
                            </div>
                            <button
                                className="btn btn--ghost btn--sm"
                                onClick={() => removeLine(index)}
                                disabled={lines.length === 1}
                                style={{ padding: 0 }}
                            >
                                <Trash2 size={16} color="var(--danger)" />
                            </button>
                        </div>
                    ))}
                </div>
            </div>

            {/* Labor */}
            <div style={{ marginBottom: '24px', paddingTop: '16px', borderTop: '1px solid var(--border-glass)' }}>
                <h4 style={{ margin: '0 0 12px 0' }}>Labor Charges</h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '16px', alignItems: 'flex-end' }}>
                    <div>
                        <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 4 }}>Labor Hours</label>
                        <input
                            className="input"
                            type="number"
                            value={laborHours}
                            onChange={(e) => setLaborHours(e.target.value)}
                        />
                    </div>
                    <div>
                        <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 4 }}>Rate (₹/hr)</label>
                        <input
                            className="input"
                            type="number"
                            value={laborRate}
                            onChange={(e) => setLaborRate(e.target.value)}
                        />
                    </div>
                    <div style={{ background: 'var(--bg-glass)', padding: '10px 16px', borderRadius: '8px', textAlign: 'right' }}>
                        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Labor Subtotal</div>
                        <div style={{ fontWeight: 600 }}>₹{(Number(laborHours) * Number(laborRate)).toLocaleString('en-IN')}</div>
                    </div>
                </div>
            </div>

            {/* Totals */}
            <div style={{
                background: 'rgba(255,255,255,0.05)',
                padding: '20px',
                borderRadius: '12px',
                marginBottom: '20px',
                border: '1px solid var(--border-glass)'
            }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Parts Subtotal:</span>
                    <span>₹{totals.partsTotal.toLocaleString('en-IN')}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Labor Subtotal:</span>
                    <span>₹{totals.laborTotal.toLocaleString('en-IN')}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                    <span style={{ color: 'var(--text-muted)' }}>GST (Estimated):</span>
                    <span>₹{totals.taxTotal.toLocaleString('en-IN')}</span>
                </div>
                <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    paddingTop: '12px',
                    borderTop: '1px solid var(--border-glass)',
                    fontSize: '1.2rem',
                    fontWeight: 700
                }}>
                    <span>Grand Total:</span>
                    <span style={{ color: 'var(--accent)' }}>₹{totals.grandTotal.toLocaleString('en-IN')}</span>
                </div>
            </div>

            <button
                className="btn btn--primary"
                onClick={handleSubmit}
                disabled={loading || lines.some(l => !l.description || !l.price)}
                style={{ width: '100%', justifyContent: 'center', height: '48px' }}
            >
                {loading ? (
                    'Creating...'
                ) : (
                    <>
                        <Calculator size={18} />
                        Create Estimate
                    </>
                )}
            </button>
        </div>
    );
}
