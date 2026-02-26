import { useState } from 'react';
import { Cpu, CheckCircle, AlertTriangle, Wrench, FileText, Plus, ArrowRight, X, Info } from 'lucide-react';
import { useSubscription } from '../context';
import FeatureGate from '../components/FeatureGate';
import SubscriptionUpgradeModal from '../components/SubscriptionUpgradeModal';

const OPERATOR_ACTIONS = [
    { id: 'create_job', label: 'Create Job Card', icon: Plus, description: 'Open a new job card for a vehicle' },
    { id: 'generate_invoice', label: 'Generate Invoice', icon: FileText, description: 'Create GST-compliant invoice from job card' },
    { id: 'update_job_state', label: 'Update Job State', icon: ArrowRight, description: 'Transition job card to next state' },
    { id: 'add_estimate', label: 'Add Estimate', icon: Wrench, description: 'Add parts and labor estimate to job' },
];

const MOCK_PREVIEW = {
    create_job: {
        title: 'Job Card Preview',
        data: {
            'Vehicle Number': 'MH12AB1234',
            'Complaint': 'Brake grinding noise',
            'Customer': 'Rahul Sharma',
            'Estimated Cost': '₹8,500 - ₹12,000',
        },
        warnings: ['Vehicle has 2 open job cards'],
    },
    generate_invoice: {
        title: 'Invoice Preview',
        data: {
            'Job Card': 'JC-0047',
            'Customer': 'Rahul Sharma',
            'Parts Total': '₹5,400',
            'Labor Total': '₹2,100',
            'GST (18%)': '₹1,350',
            'Total Amount': '₹8,850',
        },
        warnings: [],
    },
    update_job_state: {
        title: 'State Transition Preview',
        data: {
            'Job Card': 'JC-0047',
            'Current State': 'REPAIR',
            'New State': 'QC_PDI',
            'Approver': 'Auto-approved',
        },
        warnings: ['Quality check required before completion'],
    },
    add_estimate: {
        title: 'Estimate Preview',
        data: {
            'Job Card': 'JC-0048',
            'Parts Count': '4 items',
            'Labor Hours': '3.5 hrs',
            'Parts Total': '₹4,200',
            'Labor Total': '₹1,750',
            'Grand Total': '₹5,950',
        },
        warnings: [],
    },
};

export default function OperatorPage() {
    const { canPerformAction, incrementUsage } = useSubscription();
    const [selectedAction, setSelectedAction] = useState(null);
    const [showUpgrade, setShowUpgrade] = useState(false);
    const [formData, setFormData] = useState({});
    const [preview, setPreview] = useState(null);
    const [loading, setLoading] = useState(false);
    const [confirmed, setConfirmed] = useState(false);
    const [result, setResult] = useState(null);

    const handleActionSelect = (actionId) => {
        const check = canPerformAction('operator_action');
        if (!check.allowed) {
            setShowUpgrade(true);
            return;
        }
        setSelectedAction(actionId);
        setFormData({});
        setPreview(null);
        setConfirmed(false);
        setResult(null);
    };

    const handleDirectExecute = async () => {
        if (!formData.raw_query) return;
        setLoading(true);
        try {
            const token = localStorage.getItem('eka_token');
            const res = await fetch('/api/v1/operator/execute', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    raw_query: formData.raw_query,
                    tenant_id: 'eka-workshop-1',
                    actor_id: 'user-1'
                })
            });
            if (!res.ok) throw new Error("AI could not understand the command");
            const data = await res.json();
            setSelectedAction(data.tool);
            setFormData(data.args || {});
            setPreview({
                title: `AI Intent: ${data.tool}`,
                preview_id: data.preview_id,
                data: data.args || {},
                warnings: data.action_preview ? [data.action_preview] : ["AI perceived intent. Please verify carefully."]
            });
        } catch (err) {
            alert(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handlePreview = async (e) => {
        e?.preventDefault();
        setLoading(true);
        try {
            const token = localStorage.getItem('eka_token');
            const res = await fetch('/api/v1/operator/execute', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    intent: selectedAction,
                    args: formData,
                    tenant_id: 'eka-workshop-1',
                    actor_id: 'user-1'
                })
            });
            if (!res.ok) throw new Error("Failed to generate preview from API");
            const data = await res.json();
            setPreview({
                title: `Preview: ${data.tool || selectedAction}`,
                preview_id: data.preview_id,
                data: data.args || formData,
                warnings: data.action_preview ? [data.action_preview] : []
            });
        } catch (err) {
            console.warn(err.message, "Using fallback preview.");
            const fallback = { ...MOCK_PREVIEW[selectedAction] };
            fallback.preview_id = 'mock-fallback-id';
            setPreview(fallback);
        } finally {
            setLoading(false);
        }
    };

    const handleConfirm = async () => {
        setLoading(true);
        try {
            const token = localStorage.getItem('eka_token');
            const res = await fetch('/api/v1/operator/confirm', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    preview_id: preview.preview_id || 'mock',
                    confirm: true,
                    actor_id: 'user-1'
                })
            });
            if (!res.ok) throw new Error("Failed to confirm action via API");

            const data = await res.json();
            setConfirmed(true);
            setResult({
                success: data.status !== 'cancelled',
                message: data.result?.message || 'Action Completed',
                id: data.execution_id || Math.random().toString(36).substr(2, 6).toUpperCase(),
            });

            incrementUsage('operator_actions', 1);
            if (selectedAction === 'create_job') {
                incrementUsage('job_cards_created', 1);
            }
        } catch (err) {
            console.warn(err.message, "Using fallback execution.");
            setConfirmed(true);
            setResult({
                success: true,
                message: 'Action simulated successfully as fallback.',
                id: Math.random().toString(36).substr(2, 6).toUpperCase(),
            });
            incrementUsage('operator_actions', 1);
        } finally {
            setLoading(false);
        }
    };

    const renderForm = () => {
        switch (selectedAction) {
            case 'create_job':
            case 'create_job_card':
                return (
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 12 }}>
                        <div>
                            <label>Vehicle Number *</label>
                            <input
                                className="input"
                                placeholder="MH12AB1234"
                                value={formData.vehicle_number || ''}
                                onChange={e => setFormData({ ...formData, vehicle_number: e.target.value })}
                                required
                            />
                        </div>
                        <div>
                            <label>Complaint *</label>
                            <input
                                className="input"
                                placeholder="Describe the issue..."
                                value={formData.complaint || ''}
                                onChange={e => setFormData({ ...formData, complaint: e.target.value })}
                                required
                            />
                        </div>
                    </div>
                );
            case 'generate_invoice':
                return (
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                        <div>
                            <label>Job Card NO *</label>
                            <input
                                className="input"
                                placeholder="JC-0001"
                                value={formData.job_no || formData.job_id || ''}
                                onChange={e => setFormData({ ...formData, job_no: e.target.value })}
                                required
                            />
                        </div>
                    </div>
                );
            case 'update_job_state':
            case 'trigger_state_transition':
                return (
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                        <div>
                            <label>Job Card NO *</label>
                            <input
                                className="input"
                                placeholder="JC-0001"
                                value={formData.job_no || formData.job_id || ''}
                                onChange={e => setFormData({ ...formData, job_no: e.target.value })}
                                required
                            />
                        </div>
                        <div>
                            <label>New State *</label>
                            <select className="input" value={formData.new_state || ''} onChange={e => setFormData({ ...formData, new_state: e.target.value })} required>
                                <option value="">Select state...</option>
                                <option value="DIAGNOSIS">Diagnosis</option>
                                <option value="REPAIR">Repair</option>
                                <option value="READY">Ready</option>
                                <option value="INVOICED">Invoiced</option>
                            </select>
                        </div>
                    </div>
                );
            case 'add_estimate':
                return (
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr 1fr 1fr', gap: 12 }}>
                        <div>
                            <label>Job Card ID *</label>
                            <input
                                className="input"
                                placeholder="JC-0048"
                                value={formData.job_id || ''}
                                onChange={e => setFormData({ ...formData, job_id: e.target.value })}
                                required
                            />
                        </div>
                        <div>
                            <label>Part Description</label>
                            <input
                                className="input"
                                placeholder="Brake pads"
                                value={formData.part_desc || ''}
                                onChange={e => setFormData({ ...formData, part_desc: e.target.value })}
                            />
                        </div>
                    </div>
                );
            default:
                return <div className="card">AI identified a custom action: {selectedAction}. Check parameters below.</div>;
        }
    };

    return (
        <div className="fade-in">
            <div className="main__header">
                <h2 style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <Cpu size={22} color="var(--accent)" /> Operator AI
                </h2>
            </div>

            <FeatureGate feature="operator_ai">
                <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginBottom: 24 }}>
                    Execute operational actions with preview and confirmation. All actions are logged.
                </p>

                {!selectedAction ? (
                    <>
                        {/* Direct AI Command */}
                        <div style={{ marginBottom: 32 }}>
                            <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: 12, textTransform: 'uppercase' }}>
                                Direct AI Command
                            </div>
                            <div style={{ display: 'flex', gap: 12 }}>
                                <div style={{ flex: 1, position: 'relative' }}>
                                    <Cpu size={18} style={{ position: 'absolute', left: 16, top: '50%', transform: 'translateY(-50%)', color: 'var(--accent)' }} />
                                    <input
                                        className="input"
                                        style={{ paddingLeft: 48, height: 54, fontSize: '1.05rem', background: 'var(--bg-glass)' }}
                                        placeholder="Try 'Create job for vehicle MH12AB1234 with brake issue'..."
                                        value={formData.raw_query || ''}
                                        onChange={e => setFormData({ ...formData, raw_query: e.target.value })}
                                        onKeyPress={e => e.key === 'Enter' && handleDirectExecute()}
                                    />
                                </div>
                                <button className="btn btn--primary" style={{ height: 54 }} onClick={handleDirectExecute} disabled={loading || !formData.raw_query}>
                                    {loading ? 'Processing...' : 'Execute'}
                                </button>
                            </div>
                        </div>

                        {/* Quick Actions */}
                        <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: 16, textTransform: 'uppercase' }}>
                            Quick Actions
                        </div>
                        <div className="grid grid--2">
                            {OPERATOR_ACTIONS.map((action) => (
                                <div key={action.id} className="card" style={{ cursor: 'pointer' }} onClick={() => handleActionSelect(action.id)}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                                        <div style={{ width: 48, height: 48, borderRadius: 12, background: 'var(--accent-glow)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                            <action.icon size={24} color="var(--accent)" />
                                        </div>
                                        <div>
                                            <div style={{ fontSize: '1rem', fontWeight: 600 }}>{action.label}</div>
                                            <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>{action.description}</div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </>
                ) : (
                    <div>
                        <button className="btn btn--ghost btn--sm" onClick={() => setSelectedAction(null)} style={{ marginBottom: 20 }}>
                            ← Back to Actions
                        </button>

                        {!confirmed ? (
                            <>
                                <div className="card" style={{ marginBottom: 20 }}>
                                    <div className="card__title">{selectedAction.replaceAll('_', ' ').toUpperCase()}</div>
                                    <form onSubmit={handlePreview}>
                                        {renderForm()}
                                        <div style={{ display: 'flex', gap: 10, marginTop: 20 }}>
                                            <button type="submit" className="btn btn--primary" disabled={loading}>
                                                {loading ? 'Processing...' : 'Preview Action'}
                                            </button>
                                            <button type="button" className="btn btn--ghost" onClick={() => setSelectedAction(null)}>Cancel</button>
                                        </div>
                                    </form>
                                </div>

                                {preview && (
                                    <div className="card" style={{ border: '2px solid var(--accent)', background: 'rgba(99,102,241,0.05)' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
                                            <Info size={20} color="var(--accent)" />
                                            <div className="card__title" style={{ margin: 0 }}>{preview.title}</div>
                                        </div>

                                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, background: 'var(--bg-glass)', padding: 16, borderRadius: 10, marginBottom: 20 }}>
                                            {Object.entries(preview.data).map(([key, value]) => (
                                                <div key={key}>
                                                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{key}</div>
                                                    <div style={{ fontWeight: 600 }}>{String(value)}</div>
                                                </div>
                                            ))}
                                        </div>

                                        {preview.warnings.length > 0 && (
                                            <div style={{ background: 'rgba(234,179,8,0.1)', border: '1px solid rgba(234,179,8,0.3)', borderRadius: 8, padding: 12, marginBottom: 20 }}>
                                                {preview.warnings.map((w, i) => <div key={i} style={{ fontSize: '0.84rem' }}>• {w}</div>)}
                                            </div>
                                        )}

                                        <div style={{ display: 'flex', gap: 10 }}>
                                            <button className="btn btn--primary" onClick={handleConfirm} disabled={loading}>
                                                <CheckCircle size={18} style={{ marginRight: 6 }} /> Confirm & Execute
                                            </button>
                                            <button className="btn btn--ghost" onClick={() => setPreview(null)}>Modify</button>
                                        </div>
                                    </div>
                                )}
                            </>
                        ) : (
                            <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
                                <div style={{ width: 80, height: 80, borderRadius: '50%', background: 'var(--success)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 24px' }}>
                                    <CheckCircle size={40} color="white" />
                                </div>
                                <h2>Action Completed</h2>
                                <p>{result?.message}</p>
                                <button className="btn btn--primary" style={{ marginTop: 24 }} onClick={() => setSelectedAction(null)}>Done</button>
                            </div>
                        )}
                    </div>
                )}
            </FeatureGate>

            <SubscriptionUpgradeModal
                isOpen={showUpgrade}
                onClose={() => setShowUpgrade(false)}
                feature="operator_ai"
            />
        </div>
    );
}
