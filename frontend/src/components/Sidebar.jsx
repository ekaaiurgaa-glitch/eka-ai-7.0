import { NavLink, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { useAuth, useSubscription } from '../context';
import {
    LayoutDashboard, MessageSquare, ClipboardList, Car,
    Shield, LogOut, Wrench, Cpu, FileText,
    TrendingUp, CheckSquare, Crown,
} from 'lucide-react';
import SubscriptionUpgradeModal from './SubscriptionUpgradeModal';

const navItems = [
    { to: '/app', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/app/chat', icon: MessageSquare, label: 'EKA Intelligence' },
    { to: '/app/operator', icon: Cpu, label: 'Operator AI' },
    { to: '/app/jobs', icon: ClipboardList, label: 'Job Cards' },
    { to: '/app/vehicles', icon: Car, label: 'Vehicles' },
    { to: '/app/invoices', icon: FileText, label: 'Invoices' },
    { to: '/app/approvals', icon: CheckSquare, label: 'Approvals' },
    { to: '/app/analytics', icon: TrendingUp, label: 'Analytics' },
    { to: '/app/mg', icon: Shield, label: 'MG Engine' },
];

export default function Sidebar() {
    const { user, logout } = useAuth();
    const { currentPlan, isFree, getUsageDisplay } = useSubscription();
    const navigate = useNavigate();
    const [showUpgrade, setShowUpgrade] = useState(false);

    const usageData = getUsageDisplay();
    const nearLimit = usageData.some(u => u.limit && u.percent >= 80);

    const handleLogout = () => { logout(); navigate('/login'); };

    return (
        <aside className="sidebar">
            <div className="sidebar__logo">
                <Wrench size={22} color="var(--accent)" />
                <div>
                    <h1>EKA-AI</h1>
                    <span>Governed Intelligence</span>
                </div>
            </div>

            <nav className="sidebar__nav">
                {navItems.map((item) => {
                    const Icon = item.icon;
                    return (
                        <NavLink
                            key={item.to}
                            to={item.to}
                            end={item.to === '/'}
                            className={({ isActive }) =>
                                `sidebar__link ${isActive ? 'sidebar__link--active' : ''}`
                            }
                        >
                            <Icon size={18} />
                            {item.label}
                        </NavLink>
                    );
                })}
            </nav>

            {/* Usage & Subscription */}
            {isFree && (
                <div style={{ padding: '12px', margin: '8px 12px', background: 'var(--bg-glass)', borderRadius: 10 }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                        <span style={{ fontSize: '0.75rem', fontWeight: 600 }}>Free Plan</span>
                        {nearLimit && <span style={{ fontSize: '0.7rem', color: 'var(--warning)' }}>⚠️ Near limit</span>}
                    </div>
                    {usageData.slice(0, 2).map(u => (
                        <div key={u.label} style={{ marginBottom: 6 }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', marginBottom: 2 }}>
                                <span style={{ color: 'var(--text-muted)' }}>{u.label}</span>
                                <span>{u.limit ? `${u.percent.toFixed(0)}%` : '∞'}</span>
                            </div>
                            <div style={{ height: 4, borderRadius: 2, background: 'var(--bg-primary)' }}>
                                <div style={{
                                    height: '100%',
                                    width: `${Math.min(u.percent, 100)}%`,
                                    borderRadius: 2,
                                    background: u.percent >= 90 ? 'var(--danger)' : u.percent >= 70 ? 'var(--warning)' : 'var(--accent)',
                                }} />
                            </div>
                        </div>
                    ))}
                    <button
                        className="btn btn--primary btn--sm"
                        style={{ width: '100%', marginTop: 8, fontSize: '0.75rem' }}
                        onClick={() => setShowUpgrade(true)}
                    >
                        <Crown size={12} style={{ marginRight: 4 }} />
                        Upgrade
                    </button>
                </div>
            )}

            <div style={{ borderTop: '1px solid var(--border-glass)', paddingTop: 16, marginTop: 8 }}>
                <div style={{ padding: '8px 12px', marginBottom: 8 }}>
                    <div style={{ fontSize: '0.82rem', fontWeight: 600 }}>{user?.sub || 'User'}</div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                        {user?.role || 'owner'} {!isFree && <span style={{ color: 'var(--accent)' }}>• {currentPlan?.plan_name}</span>}
                    </div>
                </div>
                <button className="sidebar__link" onClick={handleLogout} style={{ border: 'none', width: '100%', cursor: 'pointer', background: 'none' }}>
                    <LogOut size={18} />
                    Sign Out
                </button>
            </div>

            <SubscriptionUpgradeModal
                isOpen={showUpgrade}
                onClose={() => setShowUpgrade(false)}
            />
        </aside>
    );
}
