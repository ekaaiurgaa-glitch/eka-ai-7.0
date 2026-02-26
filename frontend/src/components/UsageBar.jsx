import { useSubscription } from '../context/SubscriptionContext';
import { AlertTriangle, Zap, MessageSquare, ClipboardList } from 'lucide-react';

export default function UsageBar() {
    const { usage, currentPlan, getUsageDisplay, isFree } = useSubscription();
    
    if (!usage || !currentPlan) return null;

    const usageData = getUsageDisplay();
    
    const getIcon = (label) => {
        switch (label) {
            case 'AI Tokens': return MessageSquare;
            case 'Operator Actions': return Zap;
            case 'Job Cards': return ClipboardList;
            default: return Zap;
        }
    };

    return (
        <div style={{ 
            background: 'var(--bg-glass)', 
            borderRadius: 12, 
            padding: '16px 20px',
            marginBottom: 20,
            border: '1px solid var(--border-glass)',
        }}>
            <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                marginBottom: 16,
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ fontWeight: 600 }}>Usage This Cycle</span>
                    {isFree && (
                        <span 
                            className="badge"
                            style={{ 
                                background: 'var(--warning)', 
                                color: 'white',
                                fontSize: '0.65rem',
                            }}
                        >
                            FREE PLAN
                        </span>
                    )}
                </div>
                <button 
                    className="btn btn--ghost btn--sm"
                    onClick={() => window.location.href = '/app/subscription'}
                >
                    Manage Subscription
                </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                {usageData.map((item) => {
                    const Icon = getIcon(item.label);
                    const isUnlimited = item.limit === null || item.limit === undefined;
                    const percent = isUnlimited ? 0 : Math.min(item.percent, 100);
                    const isNearLimit = !isUnlimited && percent >= 80;
                    const isAtLimit = !isUnlimited && percent >= 100;
                    
                    return (
                        <div key={item.label}>
                            <div style={{ 
                                display: 'flex', 
                                justifyContent: 'space-between', 
                                alignItems: 'center',
                                marginBottom: 6,
                            }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                    <Icon size={14} color="var(--text-muted)" />
                                    <span style={{ fontSize: '0.84rem' }}>{item.label}</span>
                                    {(isNearLimit || isAtLimit) && (
                                        <AlertTriangle 
                                            size={14} 
                                            color={isAtLimit ? 'var(--danger)' : 'var(--warning)'} 
                                        />
                                    )}
                                </div>
                                <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                                    {isUnlimited ? (
                                        <span style={{ color: 'var(--success)' }}>Unlimited</span>
                                    ) : (
                                        <>
                                            <strong style={{ 
                                                color: isAtLimit ? 'var(--danger)' : isNearLimit ? 'var(--warning)' : 'inherit'
                                            }}>
                                                {item.current.toLocaleString()}
                                            </strong>
                                            {' / '}
                                            {item.limit >= 1000 ? `${(item.limit / 1000).toFixed(0)}K` : item.limit}
                                            {' '}
                                            {item.unit}
                                        </>
                                    )}
                                </div>
                            </div>
                            
                            {!isUnlimited && (
                                <div style={{ 
                                    height: 6, 
                                    borderRadius: 3, 
                                    background: 'var(--bg-primary)',
                                    overflow: 'hidden',
                                }}>
                                    <div style={{ 
                                        height: '100%', 
                                        width: `${percent}%`, 
                                        borderRadius: 3,
                                        background: isAtLimit ? 'var(--danger)' : isNearLimit ? 'var(--warning)' : 'var(--accent)',
                                        transition: 'width 0.3s ease, background 0.3s ease',
                                    }} />
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>

            {isFree && (
                <div style={{ 
                    marginTop: 16, 
                    padding: '12px 16px', 
                    background: 'rgba(99,102,241,0.1)', 
                    borderRadius: 8,
                    border: '1px dashed var(--accent)',
                }}>
                    <div style={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        justifyContent: 'space-between',
                    }}>
                        <div style={{ fontSize: '0.84rem' }}>
                            <strong>Unlock more features</strong>
                            <div style={{ color: 'var(--text-muted)', marginTop: 2 }}>
                                Upgrade to access MG Calculator, Analytics, and more
                            </div>
                        </div>
                        <button 
                            className="btn btn--primary btn--sm"
                            onClick={() => window.upgradeModal?.open?.()}
                        >
                            Upgrade
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
