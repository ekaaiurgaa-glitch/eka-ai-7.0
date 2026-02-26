import { useState } from 'react';
import { Lock, Sparkles } from 'lucide-react';
import { useSubscription, FEATURE_LABELS } from '../context';
import SubscriptionUpgradeModal from './SubscriptionUpgradeModal';

export default function FeatureGate({
    feature,
    children,
    fallback = null,
    showUpgradePrompt = true,
}) {
    const { hasFeature, canPerformAction } = useSubscription();
    const [showUpgrade, setShowUpgrade] = useState(false);

    const check = canPerformAction(feature);
    const hasAccess = hasFeature(feature);

    // If user has no access to this feature at all
    if (!hasAccess) {
        if (!showUpgradePrompt) return fallback;

        return (
            <>
                <div
                    style={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        padding: '60px 40px',
                        background: 'var(--bg-glass)',
                        borderRadius: 16,
                        border: '2px dashed var(--border-glass)',
                        textAlign: 'center',
                    }}
                >
                    <div style={{
                        width: 64,
                        height: 64,
                        borderRadius: '50%',
                        background: 'var(--accent-glow)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        marginBottom: 20,
                    }}>
                        <Lock size={28} color="var(--accent)" />
                    </div>
                    <h3 style={{ margin: '0 0 8px 0' }}>Premium Feature</h3>
                    <p style={{ color: 'var(--text-muted)', marginBottom: 20, maxWidth: 400 }}>
                        {FEATURE_LABELS[feature]} is available on paid plans.
                        Upgrade to unlock this and other premium features.
                    </p>
                    <button
                        className="btn btn--primary"
                        onClick={() => setShowUpgrade(true)}
                    >
                        <Sparkles size={18} style={{ marginRight: 8 }} />
                        Upgrade to Unlock
                    </button>
                </div>
                <SubscriptionUpgradeModal
                    isOpen={showUpgrade}
                    onClose={() => setShowUpgrade(false)}
                    feature={feature}
                />
            </>
        );
    }

    // If user has access but reached a limit
    if (!check.allowed) {
        return (
            <>
                <div
                    style={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        padding: '40px',
                        background: 'rgba(239,68,68,0.05)',
                        borderRadius: 16,
                        border: '1px solid rgba(239,68,68,0.2)',
                        textAlign: 'center',
                    }}
                >
                    <div style={{ color: 'var(--danger)', marginBottom: 12, fontWeight: 600 }}>
                        ⚠️ Limit Reached
                    </div>
                    <p style={{ color: 'var(--text-secondary)', marginBottom: 16 }}>
                        {check.reason}
                    </p>
                    {check.upgrade && (
                        <button
                            className="btn btn--primary"
                            onClick={() => setShowUpgrade(true)}
                        >
                            <Sparkles size={18} style={{ marginRight: 8 }} />
                            Upgrade Plan
                        </button>
                    )}
                </div>
                <SubscriptionUpgradeModal
                    isOpen={showUpgrade}
                    onClose={() => setShowUpgrade(false)}
                    feature={feature}
                />
            </>
        );
    }

    // If user has access but nearing limit
    if (check.warning) {
        return (
            <>
                <div style={{
                    background: 'rgba(234,179,8,0.1)',
                    border: '1px solid rgba(234,179,8,0.3)',
                    borderRadius: 8,
                    padding: '12px 16px',
                    marginBottom: 16,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ fontSize: '1.2rem' }}>⚠️</span>
                        <span style={{ fontSize: '0.86rem' }}>{check.warning}</span>
                    </div>
                    {check.upgrade && (
                        <button
                            className="btn btn--ghost btn--sm"
                            onClick={() => setShowUpgrade(true)}
                            style={{ color: 'var(--warning)' }}
                        >
                            Upgrade
                        </button>
                    )}
                </div>
                {children}
                <SubscriptionUpgradeModal
                    isOpen={showUpgrade}
                    onClose={() => setShowUpgrade(false)}
                    feature={feature}
                />
            </>
        );
    }

    // Normal access
    return children;
}
