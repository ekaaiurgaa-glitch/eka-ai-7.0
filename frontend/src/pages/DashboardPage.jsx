import { useState, useEffect } from 'react';
import { TrendingUp, ClipboardList, Clock, AlertTriangle, DollarSign, Users, Activity } from 'lucide-react';

export default function DashboardPage() {
    const [kpis, setKpis] = useState(null);

    useEffect(() => {
        // Simulated KPIs (would come from /api/v1/dashboards/workshop)
        setKpis({
            monthly_revenue: 487500,
            profit_margin_pct: 34.5,
            jobs_open: 8,
            jobs_in_progress: 14,
            jobs_closed_today: 6,
            pending_approvals: 3,
            avg_tat_hours: 4.2,
            mg_contracts_active: 23,
        });
    }, []);

    if (!kpis) return null;

    const statCards = [
        { label: 'Monthly Revenue', value: `₹${(kpis.monthly_revenue / 1000).toFixed(0)}K`, icon: DollarSign, color: 'var(--success)' },
        { label: 'Profit Margin', value: `${kpis.profit_margin_pct}%`, icon: TrendingUp, color: 'var(--accent-hover)' },
        { label: 'Open Jobs', value: kpis.jobs_open, icon: ClipboardList, color: 'var(--info)' },
        { label: 'Avg TAT', value: `${kpis.avg_tat_hours}h`, icon: Clock, color: 'var(--warning)' },
    ];

    const activityItems = [
        { time: '2 min ago', text: 'Job #JC-0047 moved to REPAIR', type: 'info' },
        { time: '15 min ago', text: 'Invoice INV-0023 generated — ₹12,400', type: 'success' },
        { time: '32 min ago', text: 'MG Contract MG-0012 activated for KA-05-MJ-4521', type: 'accent' },
        { time: '1 hr ago', text: 'Customer approved estimate for JC-0045', type: 'success' },
        { time: '2 hr ago', text: 'Low stock alert: Brake Pads (Qty: 2)', type: 'warning' },
        { time: '3 hr ago', text: 'New job card JC-0046 created', type: 'info' },
    ];

    return (
        <div className="fade-in">
            <div className="main__header">
                <div>
                    <h2>Workshop Dashboard</h2>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: 4 }}>
                        Real-time overview • {new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}
                    </p>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span className="status-dot status-dot--open" style={{ animation: 'pulse 2s infinite' }} />
                    <span style={{ fontSize: '0.82rem', color: 'var(--success)' }}>System Operational</span>
                </div>
            </div>

            {/* KPI Cards */}
            <div className="grid grid--4" style={{ marginBottom: 28 }}>
                {statCards.map((s, i) => (
                    <div className="card" key={i}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                            <div>
                                <div className="card__title">{s.label}</div>
                                <div className="card__value">{s.value}</div>
                            </div>
                            <div style={{
                                width: 42, height: 42, borderRadius: 12,
                                background: `${s.color}15`, display: 'flex', alignItems: 'center', justifyContent: 'center'
                            }}>
                                <s.icon size={20} color={s.color} />
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Bottom Section */}
            <div className="grid grid--2">
                {/* Job Status Breakdown */}
                <div className="card">
                    <div className="card__title">Job Status Breakdown</div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 14, marginTop: 8 }}>
                        {[
                            { label: 'Open', count: kpis.jobs_open, color: 'var(--info)', pct: 20 },
                            { label: 'In Progress', count: kpis.jobs_in_progress, color: 'var(--warning)', pct: 45 },
                            { label: 'Pending Approval', count: kpis.pending_approvals, color: '#a78bfa', pct: 10 },
                            { label: 'Closed Today', count: kpis.jobs_closed_today, color: 'var(--success)', pct: 25 },
                        ].map((s, i) => (
                            <div key={i}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                                    <span style={{ fontSize: '0.84rem', color: 'var(--text-secondary)' }}>{s.label}</span>
                                    <span style={{ fontSize: '0.84rem', fontWeight: 600, color: s.color }}>{s.count}</span>
                                </div>
                                <div style={{ height: 6, borderRadius: 3, background: 'var(--bg-glass)' }}>
                                    <div style={{ height: '100%', width: `${s.pct}%`, borderRadius: 3, background: s.color, transition: 'width 0.8s ease' }} />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Activity Feed */}
                <div className="card">
                    <div className="card__title">Recent Activity</div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginTop: 8 }}>
                        {activityItems.map((item, i) => (
                            <div key={i} style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
                                <div style={{
                                    width: 8, height: 8, borderRadius: '50%', marginTop: 7, flexShrink: 0,
                                    background: item.type === 'success' ? 'var(--success)' :
                                        item.type === 'warning' ? 'var(--warning)' :
                                            item.type === 'accent' ? 'var(--accent)' : 'var(--info)'
                                }} />
                                <div>
                                    <div style={{ fontSize: '0.86rem', color: 'var(--text-secondary)' }}>{item.text}</div>
                                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: 2 }}>{item.time}</div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
