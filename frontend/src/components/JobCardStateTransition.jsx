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
                    background: (STATE_CONFIG[currentState]?.color || '#888') + '20',
                    color: STATE_CONFIG[currentState]?.color || '#888',
                    fontWeight: 600
                }}>
                    {STATE_CONFIG[currentState]?.label || currentState}
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
                            {STATE_CONFIG[state]?.label || state}
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
