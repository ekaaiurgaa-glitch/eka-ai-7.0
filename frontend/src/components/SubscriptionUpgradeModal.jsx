import { X, Check, Sparkles, AlertCircle } from 'lucide-react';
import { useSubscription, SUBSCRIPTION_PLANS, FEATURE_LABELS } from '../context/SubscriptionContext';

export default function SubscriptionUpgradeModal({ isOpen, onClose, feature }) {
    const { currentPlan, subscription } = useSubscription();
    
    if (!isOpen) return null;

    const plans = Object.values(SUBSCRIPTION_PLANS);
    const currentPlanId = currentPlan?.id;

    const formatPrice = (price) => {
        if (price === 0) return 'Free';
        return `₹${price.toLocaleString('en-IN')}/mo`;
    };

    const formatLimit = (limit) => {
        if (limit === null || limit === undefined) return 'Unlimited';
        if (limit >= 1000000) return `${(limit / 1000000).toFixed(1)}M`;
        if (limit >= 1000) return `${(limit / 1000).toFixed(0)}K`;
        return limit.toString();
    };

    return (
        <div 
            style={{
                position: 'fixed',
                top: 0, left: 0, right: 0, bottom: 0,
                background: 'rgba(0,0,0,0.8)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 1000,
                padding: 20,
            }}
            onClick={onClose}
        >
            <div 
                style={{ 
                    width: '100%', 
                    maxWidth: 900, 
                    maxHeight: '90vh',
                    overflow: 'auto',
                    background: 'var(--bg-secondary)',
                    borderRadius: 16,
                    border: '1px solid var(--border-glass)',
                }}
                onClick={e => e.stopPropagation()}
            >
                {/* Header */}
                <div style={{ 
                    padding: '24px 32px', 
                    borderBottom: '1px solid var(--border-glass)',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                }}>
                    <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                            <Sparkles size={24} color="var(--accent)" />
                            <h2 style={{ margin: 0 }}>Upgrade Your Plan</h2>
                        </div>
                        {feature && (
                            <p style={{ margin: '8px 0 0 0', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                                <AlertCircle size={14} style={{ display: 'inline', marginRight: 6 }} />
                                {FEATURE_LABELS[feature]} requires an upgrade
                            </p>
                        )}
                    </div>
                    <button 
                        onClick={onClose}
                        style={{ 
                            background: 'none', 
                            border: 'none', 
                            color: 'var(--text-muted)', 
                            cursor: 'pointer',
                            padding: 8,
                        }}
                    >
                        <X size={24} />
                    </button>
                </div>

                {/* Plans Grid */}
                <div style={{ padding: 32 }}>
                    <div style={{ 
                        display: 'grid', 
                        gridTemplateColumns: 'repeat(4, 1fr)', 
                        gap: 16,
                    }}>
                        {plans.map((plan) => {
                            const isCurrent = plan.id === currentPlanId;
                            const isRecommended = plan.id === 'professional';
                            
                            return (
                                <div 
                                    key={plan.id}
                                    style={{
                                        background: isCurrent ? 'var(--accent-glow)' : 'var(--bg-primary)',
                                        border: `2px solid ${isCurrent ? 'var(--accent)' : isRecommended ? 'var(--success)' : 'var(--border-glass)'}`,
                                        borderRadius: 12,
                                        padding: 20,
                                        position: 'relative',
                                    }}
                                >
                                    {isCurrent && (
                                        <div style={{
                                            position: 'absolute',
                                            top: -10,
                                            left: '50%',
                                            transform: 'translateX(-50%)',
                                            background: 'var(--accent)',
                                            color: 'white',
                                            padding: '2px 12px',
                                            borderRadius: 10,
                                            fontSize: '0.7rem',
                                            fontWeight: 600,
                                        }}>
                                            CURRENT
                                        </div>
                                    )}
                                    {isRecommended && !isCurrent && (
                                        <div style={{
                                            position: 'absolute',
                                            top: -10,
                                            left: '50%',
                                            transform: 'translateX(-50%)',
                                            background: 'var(--success)',
                                            color: 'white',
                                            padding: '2px 12px',
                                            borderRadius: 10,
                                            fontSize: '0.7rem',
                                            fontWeight: 600,
                                        }}>
                                            RECOMMENDED
                                        </div>
                                    )}
                                    
                                    <h3 style={{ margin: '0 0 8px 0', fontSize: '1.1rem' }}>{plan.plan_name}</h3>
                                    <div style={{ 
                                        fontSize: '1.5rem', 
                                        fontWeight: 700, 
                                        color: 'var(--accent-hover)',
                                        marginBottom: 4,
                                    }}>
                                        {formatPrice(plan.monthly_price_inr)}
                                    </div>
                                    <p style={{ 
                                        fontSize: '0.78rem', 
                                        color: 'var(--text-muted)', 
                                        marginBottom: 16,
                                        minHeight: 32,
                                    }}>
                                        {plan.description}
                                    </p>

                                    {/* Limits */}
                                    <div style={{ marginBottom: 16 }}>
                                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 8 }}>Includes:</div>
                                        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                                            <div style={{ fontSize: '0.82rem' }}>
                                                <strong>{formatLimit(plan.token_limit)}</strong> AI tokens/mo
                                            </div>
                                            <div style={{ fontSize: '0.82rem' }}>
                                                <strong>{formatLimit(plan.operator_actions_per_day)}</strong> operator actions/day
                                            </div>
                                            <div style={{ fontSize: '0.82rem' }}>
                                                <strong>{formatLimit(plan.job_card_limit_per_month)}</strong> job cards/mo
                                            </div>
                                        </div>
                                    </div>

                                    {/* Features */}
                                    <div style={{ marginBottom: 16 }}>
                                        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                                            {Object.entries(plan.features).map(([key, enabled]) => (
                                                <div 
                                                    key={key}
                                                    style={{ 
                                                        display: 'flex', 
                                                        alignItems: 'center', 
                                                        gap: 6,
                                                        fontSize: '0.78rem',
                                                        color: enabled ? 'var(--text-secondary)' : 'var(--text-muted)',
                                                        textDecoration: enabled ? 'none' : 'line-through',
                                                    }}
                                                >
                                                    <Check size={12} color={enabled ? 'var(--success)' : 'var(--text-muted)'} />
                                                    {FEATURE_LABELS[key]}
                                                </div>
                                            ))}
                                        </div>
                                    </div>

                                    {/* CTA Button */}
                                    <button 
                                        className={`btn ${isCurrent ? 'btn--ghost' : 'btn--primary'}`}
                                        style={{ width: '100%' }}
                                        disabled={isCurrent}
                                        onClick={() => {
                                            alert(`Upgrade to ${plan.plan_name} - Integration with payment gateway required`);
                                        }}
                                    >
                                        {isCurrent ? 'Current Plan' : 'Upgrade'}
                                    </button>
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* Footer */}
                <div style={{ 
                    padding: '16px 32px', 
                    borderTop: '1px solid var(--border-glass)',
                    textAlign: 'center',
                    color: 'var(--text-muted)',
                    fontSize: '0.82rem',
                }}>
                    All plans include core features: Dashboard, Job Cards, Vehicles, and EKA Intelligence.
                    <br />
                    Need a custom plan? Contact us at enterprise@eka-ai.in
                </div>
            </div>
        </div>
    );
}
