import { useState, useEffect } from 'react';
import { TrendingUp, BarChart3, PieChart, DollarSign, Activity, Users, Wrench, Clock } from 'lucide-react';
import FeatureGate from '../components/FeatureGate';

const MOCK_ANALYTICS = {
    unit_economics: {
        total_revenue: 2450000,
        total_cost: 1837500,
        gross_margin: 612500,
        margin_pct: 25.0,
        jobs_completed: 156,
        avg_revenue_per_job: 15705,
        avg_cost_per_job: 11779,
    },
    token_projections: [
        { month: 'Jan 2026', tokens: 45000, cost: 225 },
        { month: 'Feb 2026', tokens: 52000, cost: 260 },
        { month: 'Mar 2026', tokens: 48000, cost: 240 },
        { month: 'Apr 2026', tokens: 55000, cost: 275 },
        { month: 'May 2026', tokens: 61000, cost: 305 },
        { month: 'Jun 2026', tokens: 58000, cost: 290 },
    ],
    job_breakdown: [
        { state: 'OPEN', count: 8, revenue: 0 },
        { state: 'REPAIR', count: 14, revenue: 125000 },
        { state: 'QC_PDI', count: 5, revenue: 85000 },
        { state: 'BILLING', count: 6, revenue: 94000 },
        { state: 'CLOSED', count: 123, revenue: 2146000 },
    ],
    top_services: [
        { name: 'General Service', count: 45, revenue: 450000 },
        { name: 'Brake Repair', count: 32, revenue: 384000 },
        { name: 'AC Service', count: 28, revenue: 336000 },
        { name: 'Clutch Replacement', count: 18, revenue: 270000 },
        { name: 'Suspension Work', count: 15, revenue: 225000 },
    ],
};

export default function AnalyticsPage() {
    const [timeRange, setTimeRange] = useState('30d');
    const [data] = useState(MOCK_ANALYTICS);
    // const [loading, setLoading] = useState(false);

    useEffect(() => {
        // Simulate API call
        // setLoading(true);
        // setTimeout(() => setLoading(false), 500);
    }, [timeRange]);

    const formatCurrency = (val) => `₹${(val / 1000).toFixed(1)}K`;

    return (
        <div className="fade-in">
            <div className="main__header">
                <h2 style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <BarChart3 size={22} color="var(--accent)" /> Analytics & Insights
                </h2>
            </div>

            <FeatureGate feature="analytics">
                <div>
                    <div className="main__header" style={{ padding: 0, marginBottom: 24 }}>
                        <select
                            className="input"
                            style={{ width: 140 }}
                            value={timeRange}
                            onChange={e => setTimeRange(e.target.value)}
                        >
                            <option value="7d">Last 7 Days</option>
                            <option value="30d">Last 30 Days</option>
                            <option value="90d">Last 90 Days</option>
                            <option value="1y">Last Year</option>
                        </select>
                    </div>

                    {/* Unit Economics KPI Cards */}
                    <div className="grid grid--4" style={{ marginBottom: 24 }}>
                        {[
                            {
                                label: 'Total Revenue',
                                value: formatCurrency(data.unit_economics.total_revenue),
                                icon: DollarSign,
                                change: '+12.5%',
                                changeColor: 'var(--success)'
                            },
                            {
                                label: 'Gross Margin',
                                value: `${data.unit_economics.margin_pct}%`,
                                icon: TrendingUp,
                                change: '+2.1%',
                                changeColor: 'var(--success)'
                            },
                            {
                                label: 'Jobs Completed',
                                value: data.unit_economics.jobs_completed,
                                icon: Wrench,
                                change: '+8.3%',
                                changeColor: 'var(--success)'
                            },
                            {
                                label: 'Avg Revenue/Job',
                                value: formatCurrency(data.unit_economics.avg_revenue_per_job),
                                icon: Activity,
                                change: '-1.2%',
                                changeColor: 'var(--danger)'
                            },
                        ].map((stat, i) => (
                            <div className="card" key={i}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                    <div>
                                        <div className="card__title" style={{ fontSize: '0.78rem', marginBottom: 8 }}>{stat.label}</div>
                                        <div className="card__value" style={{ fontSize: '1.5rem' }}>{stat.value}</div>
                                        <div style={{ fontSize: '0.75rem', color: stat.changeColor, marginTop: 6 }}>{stat.change} vs last period</div>
                                    </div>
                                    <div style={{
                                        width: 42, height: 42, borderRadius: 12,
                                        background: 'var(--accent-glow)', display: 'flex', alignItems: 'center', justifyContent: 'center'
                                    }}>
                                        <stat.icon size={20} color="var(--accent)" />
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Charts Row */}
                    <div className="grid grid--2" style={{ marginBottom: 24 }}>
                        {/* Job Status Breakdown */}
                        <div className="card">
                            <div className="card__title" style={{ marginBottom: 20 }}>Job Status Distribution</div>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                                {data.job_breakdown.map((item, i) => {
                                    const total = data.job_breakdown.reduce((a, b) => a + b.count, 0);
                                    const pct = (item.count / total * 100).toFixed(1);
                                    const colors = ['var(--info)', 'var(--warning)', 'var(--accent)', '#a78bfa', 'var(--success)'];
                                    return (
                                        <div key={i}>
                                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                                                <span style={{ fontSize: '0.84rem', fontWeight: 500 }}>{item.state}</span>
                                                <span style={{ fontSize: '0.84rem', color: 'var(--text-muted)' }}>{item.count} jobs ({pct}%)</span>
                                            </div>
                                            <div style={{ height: 8, borderRadius: 4, background: 'var(--bg-glass)', overflow: 'hidden' }}>
                                                <div style={{
                                                    height: '100%',
                                                    width: `${pct}%`,
                                                    background: colors[i % colors.length],
                                                    transition: 'width 0.8s ease'
                                                }} />
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>

                        {/* Top Services */}
                        <div className="card">
                            <div className="card__title" style={{ marginBottom: 20 }}>Top Services by Revenue</div>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                                {data.top_services.map((service, i) => (
                                    <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                                        <div style={{
                                            width: 32, height: 32, borderRadius: 8,
                                            background: 'var(--accent-glow)',
                                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                                            fontSize: '0.8rem', fontWeight: 700, color: 'var(--accent)'
                                        }}>
                                            {i + 1}
                                        </div>
                                        <div style={{ flex: 1 }}>
                                            <div style={{ fontSize: '0.86rem', fontWeight: 500 }}>{service.name}</div>
                                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{service.count} jobs</div>
                                        </div>
                                        <div style={{ textAlign: 'right' }}>
                                            <div style={{ fontSize: '0.86rem', fontWeight: 600 }}>{formatCurrency(service.revenue)}</div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Token Usage Projection */}
                    <div className="card" style={{ marginBottom: 24 }}>
                        <div className="card__title" style={{ marginBottom: 20 }}>AI Token Usage Projection</div>
                        <div style={{ display: 'flex', alignItems: 'flex-end', gap: 20, height: 200, padding: '0 10px' }}>
                            {data.token_projections.map((proj, i) => {
                                const maxTokens = Math.max(...data.token_projections.map(p => p.tokens));
                                const height = (proj.tokens / maxTokens * 100).toFixed(1);
                                return (
                                    <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                                        <div style={{
                                            width: '100%',
                                            height: `${height * 1.5}px`,
                                            background: 'linear-gradient(180deg, var(--accent) 0%, var(--accent-hover) 100%)',
                                            borderRadius: '6px 6px 0 0',
                                            minHeight: 20
                                        }} />
                                        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: 8, textAlign: 'center' }}>
                                            {proj.month.split(' ')[0]}
                                        </div>
                                        <div style={{ fontSize: '0.7rem', color: 'var(--accent)', marginTop: 2 }}>
                                            {proj.tokens.toLocaleString()}
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                        <div style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            marginTop: 20,
                            padding: '16px',
                            background: 'var(--bg-glass)',
                            borderRadius: 10
                        }}>
                            <div>
                                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Projected 6-Month Cost</div>
                                <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--accent-hover)', marginTop: 4 }}>
                                    ${data.token_projections.reduce((a, b) => a + b.cost, 0).toLocaleString()}
                                </div>
                            </div>
                            <div style={{ textAlign: 'right' }}>
                                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Total Tokens</div>
                                <div style={{ fontSize: '1.2rem', fontWeight: 700, marginTop: 4 }}>
                                    {data.token_projections.reduce((a, b) => a + b.tokens, 0).toLocaleString()}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Cost Breakdown */}
                    <div className="card">
                        <div className="card__title" style={{ marginBottom: 20 }}>Unit Economics Breakdown</div>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 20 }}>
                            <div style={{ textAlign: 'center', padding: '20px', background: 'var(--bg-glass)', borderRadius: 12 }}>
                                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 8 }}>Revenue</div>
                                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--success)' }}>
                                    {formatCurrency(data.unit_economics.total_revenue)}
                                </div>
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 4 }}>100%</div>
                            </div>
                            <div style={{ textAlign: 'center', padding: '20px', background: 'var(--bg-glass)', borderRadius: 12 }}>
                                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 8 }}>Costs</div>
                                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--danger)' }}>
                                    {formatCurrency(data.unit_economics.total_cost)}
                                </div>
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 4 }}>
                                    {((data.unit_economics.total_cost / data.unit_economics.total_revenue) * 100).toFixed(1)}%
                                </div>
                            </div>
                            <div style={{ textAlign: 'center', padding: '20px', background: 'var(--bg-glass)', borderRadius: 12 }}>
                                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 8 }}>Gross Profit</div>
                                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--accent)' }}>
                                    {formatCurrency(data.unit_economics.gross_margin)}
                                </div>
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 4 }}>
                                    {data.unit_economics.margin_pct}%
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </FeatureGate>
        </div>
    );
}
