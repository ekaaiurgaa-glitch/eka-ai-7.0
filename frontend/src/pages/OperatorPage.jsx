import { useState, useEffect } from 'react';
import { Cpu, CheckCircle, AlertTriangle, Wrench, FileText, Plus, ArrowRight, X, Info } from 'lucide-react';
import { useSubscription } from '../context/SubscriptionContext';
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
    const [limitCheck, setLimitCheck] = useState(null);
    const [formData, setFormData] = useState({});
    const [preview, setPreview] = useState(null);
    const [loading, setLoading] = useState(false);
    const [confirmed, setConfirmed] = useState(false);
    const [result, setResult] = useState(null);

    const handleActionSelect = (actionId) => {
        // Check limits before allowing action selection
        const check = canPerformAction('operator_action');
        if (!check.allowed) {
            setLimitCheck(check);
            setShowUpgrade(true);
            return;
        }
        setSelectedAction(actionId);
        setFormData({});
        setPreview(null);
        setConfirmed(false);
        setResult(null);
        setLimitCheck(check);
    };

    const handlePreview = async (e) => {
        e.preventDefault();
        setLoading(true);
        // Simulate API call for preview
        setTimeout(() => {
            setPreview(MOCK_PREVIEW[selectedAction]);
            setLoading(false);
        }, 800);
    };

    const handleConfirm = async () => {
        setLoading(true);
        // Simulate execution
        setTimeout(() => {
            setConfirmed(true);
            setResult({
                success: true,
                message: selectedAction === 'create_job' ? 'Job card JC-0049 created successfully' :
                         selectedAction === 'generate_invoice' ? 'Invoice INV-0025 generated' :
                         selectedAction === 'update_job_state' ? 'Job state updated to QC_PDI' :
                         'Estimate added to job card',
                id: Math.random().toString(36).substr(2, 6).toUpperCase(),
            });
            // Increment usage after successful action
            incrementUsage('operator_actions', 1);
            if (selectedAction === 'create_job') {
                incrementUsage('job_cards_created', 1);
            }
            setLoading(false);
        }, 1200);
    };

    const renderForm = () => {
        switch (selectedAction) {
            case 'create_job':
                return (
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 12 }}>
                        <div>
                            <label>Vehicle Number *</label>
                            <input 
                                className="input" 
                                placeholder="MH12AB1234"
                                value={formData.vehicle_number || ''}
                                onChange={e => setFormData({...formData, vehicle_number: e.target.value})}
                                required
                            />
                        </div>
                        <div>
                            <label>Complaint *</label>
                            <input 
                                className="input" 
                                placeholder="Describe the issue..."
                                value={formData.complaint || ''}
                                onChange={e => setFormData({...formData, complaint: e.target.value})}
                                required
                            />
                        </div>
                        <div>
                            <label>Customer Name</label>
                            <input 
                                className="input" 
                                placeholder="Customer name"
                                value={formData.customer || ''}
                                onChange={e => setFormData({...formData, customer: e.target.value})}
                            />
                        </div>
                        <div>
                            <label>Priority</label>
                            <select className="input" value={formData.priority || 'normal'} onChange={e => setFormData({...formData, priority: e.target.value})}>
                                <option value="low">Low</option>
                                <option value="normal">Normal</option>
                                <option value="high">High</option>
                                <option value="urgent">Urgent</option>
                            </select>
                        </div>
                    </div>
                );
            case 'generate_invoice':
                return (
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                        <div>
                            <label>Job Card ID *</label>
                            <input 
                                className="input" 
                                placeholder="JC-0047"
                                value={formData.job_id || ''}
                                onChange={e => setFormData({...formData, job_id: e.target.value})}
                                required
                            />
                        </div>
                        <div>
                            <label>Payment Terms</label>
                            <select className="input" value={formData.terms || 'immediate'} onChange={e => setFormData({...formData, terms: e.target.value})}>
                                <option value="immediate">Immediate</option>
                                <option value="net15">Net 15 Days</option>
                                <option value="net30">Net 30 Days</option>
                            </select>
                        </div>
                    </div>
                );
            case 'update_job_state':
                return (
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                        <div>
                            <label>Job Card ID *</label>
                            <input 
                                className="input" 
                                placeholder="JC-0047"
                                value={formData.job_id || ''}
                                onChange={e => setFormData({...formData, job_id: e.target.value})}
                                required
                            />
                        </div>
                        <div>
                            <label>New State *</label>
                            <select className="input" value={formData.new_state || ''} onChange={e => setFormData({...formData, new_state: e.target.value})} required>
                                <option value="">Select state...</option>
                                <option value="DIAGNOSIS">Diagnosis</option>
                                <option value="ESTIMATE_PENDING">Estimate Pending</option>
                                <option value="APPROVAL_PENDING">Approval Pending</option>
                                <option value="APPROVED">Approved</option>
                                <option value="REPAIR">Repair</option>
                                <option value="QC_PDI">QC / PDI</option>
                                <option value="READY">Ready</option>
                                <option value="BILLING">Billing</option>
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
                                onChange={e => setFormData({...formData, job_id: e.target.value})}
                                required
                            />
                        </div>
                        <div>
                            <label>Part Description</label>
                            <input 
                                className="input" 
                                placeholder="Brake pads - front"
                                value={formData.part_desc || ''}
                                onChange={e => setFormData({...formData, part_desc: e.target.value})}
                            />
                        </div>
                        <div>
                            <label>Quantity</label>
                            <input 
                                className="input" 
                                type="number"
                                placeholder="1"
                                value={formData.qty || ''}
                                onChange={e => setFormData({...formData, qty: e.target.value})}
                            />
                        </div>
                        <div>
                            <label>Unit Price</label>
                            <input 
                                className="input" 
                                type="number"
                                placeholder="₹"
                                value={formData.price || ''}
                                onChange={e => setFormData({...formData, price: e.target.value})}
                            />
                        </div>
                    </div>
                );
            default:
                return null;
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
                Execute operational actions with preview and confirmation. All actions are logged and require explicit approval.
            </p>

            {!selectedAction ? (
                // Action Selection Grid
                <div className="grid grid--2">
                    {OPERATOR_ACTIONS.map((action) => (
                        <div 
                            key={action.id} 
                            className="card" 
                            style={{ cursor: 'pointer', transition: 'all 0.2s' }}
                            onClick={() => handleActionSelect(action.id)}
                            onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-2px)'}
                            onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0)'}
                        >
                            <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                                <div style={{
                                    width: 48, height: 48, borderRadius: 12,
                                    background: 'var(--accent-glow)', display: 'flex', alignItems: 'center', justifyContent: 'center'
                                }}>
                                    <action.icon size={24} color="var(--accent)" />
                                </div>
                                <div>
                                    <div style={{ fontSize: '1rem', fontWeight: 600 }}>{action.label}</div>
                                    <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: 2 }}>{action.description}</div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                // Action Form & Preview
                <div>
                    <button 
                        className="btn btn--ghost btn--sm" 
                        onClick={() => setSelectedAction(null)}
                        style={{ marginBottom: 20 }}
                    >
                        ← Back to Actions
                    </button>

                    {!confirmed ? (
                        <>
                            {/* Input Form */}
                            <div className="card" style={{ marginBottom: 20 }}>
                                <div className="card__title">
                                    {OPERATOR_ACTIONS.find(a => a.id === selectedAction)?.label}
                                </div>
                                <form onSubmit={handlePreview}>
                                    {renderForm()}
                                    <div style={{ display: 'flex', gap: 10, marginTop: 20 }}>
                                        <button 
                                            type="submit" 
                                            className="btn btn--primary"
                                            disabled={loading}
                                        >
                                            {loading ? 'Generating Preview...' : 'Preview Action'}
                                        </button>
                                        <button 
                                            type="button" 
                                            className="btn btn--ghost"
                                            onClick={() => setSelectedAction(null)}
                                        >
                                            Cancel
                                        </button>
                                    </div>
                                </form>
                            </div>

                            {/* Preview Panel */}
                            {preview && (
                                <div className="card" style={{ border: '2px solid var(--accent)', background: 'rgba(99,102,241,0.05)' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
                                        <Info size={20} color="var(--accent)" />
                                        <div className="card__title" style={{ margin: 0 }}>{preview.title}</div>
                                    </div>

                                    {preview.warnings.length > 0 && (
                                        <div style={{ 
                                            background: 'rgba(234,179,8,0.1)', 
                                            border: '1px solid rgba(234,179,8,0.3)',
                                            borderRadius: 8,
                                            padding: '12px 16px',
                                            marginBottom: 16
                                        }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                                                <AlertTriangle size={16} color="var(--warning)" />
                                                <span style={{ fontWeight: 600, color: 'var(--warning)' }}>Warnings</span>
                                            </div>
                                            {preview.warnings.map((w, i) => (
                                                <div key={i} style={{ fontSize: '0.84rem', marginLeft: 24 }}>• {w}</div>
                                            ))}
                                        </div>
                                    )}

                                    <div style={{ 
                                        display: 'grid', 
                                        gridTemplateColumns: 'repeat(2, 1fr)', 
                                        gap: 12,
                                        background: 'var(--bg-glass)',
                                        padding: 16,
                                        borderRadius: 10,
                                        marginBottom: 20
                                    }}>
                                        {Object.entries(preview.data).map(([key, value]) => (
                                            <div key={key}>
                                                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{key}</div>
                                                <div style={{ fontWeight: 600, marginTop: 2 }}>{value}</div>
                                            </div>
                                        ))}
                                    </div>

                                    <div style={{ 
                                        display: 'flex', 
                                        alignItems: 'center', 
                                        gap: 12,
                                        padding: '16px',
                                        background: 'var(--bg-secondary)',
                                        borderRadius: 10,
                                        marginBottom: 16
                                    }}>
                                        <input 
                                            type="checkbox" 
                                            id="confirm" 
                                            style={{ width: 20, height: 20, accentColor: 'var(--accent)' }}
                                        />
                                        <label htmlFor="confirm" style={{ fontSize: '0.9rem', cursor: 'pointer' }}>
                                            I confirm this action is correct and authorize execution
                                        </label>
                                    </div>

                                    <div style={{ display: 'flex', gap: 10 }}>
                                        <button 
                                            className="btn btn--primary"
                                            onClick={handleConfirm}
                                            disabled={loading}
                                        >
                                            <CheckCircle size={18} style={{ marginRight: 6 }} />
                                            {loading ? 'Executing...' : 'Confirm & Execute'}
                                        </button>
                                        <button 
                                            className="btn btn--ghost"
                                            onClick={() => setPreview(null)}
                                        >
                                            Modify
                                        </button>
                                    </div>
                                </div>
                            )}
                        </>
                    ) : (
                        // Success Result
                        <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
                            <div style={{
                                width: 80, height: 80, borderRadius: '50%',
                                background: 'var(--success)',
                                display: 'flex', alignItems: 'center', justifyContent: 'center',
                                margin: '0 auto 24px'
                            }}>
                                <CheckCircle size={40} color="white" />
                            </div>
                            <div style={{ fontSize: '1.3rem', fontWeight: 700, marginBottom: 8 }}>Action Completed Successfully</div>
                            <div style={{ color: 'var(--text-secondary)', marginBottom: 24 }}>{result?.message}</div>
                            <div style={{ 
                                background: 'var(--bg-glass)', 
                                padding: '16px 24px', 
                                borderRadius: 10,
                                display: 'inline-block',
                                marginBottom: 24
                            }}>
                                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Reference ID</div>
                                <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--accent)' }}>{result?.id}</div>
                            </div>
                            <div>
                                <button className="btn btn--primary" onClick={() => setSelectedAction(null)}>
                                    Execute Another Action
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            )}
            
            <SubscriptionUpgradeModal 
                isOpen={showUpgrade} 
                onClose={() => setShowUpgrade(false)} 
                feature="operator_ai"
            />
            </FeatureGate>
        </div>
    );
}
