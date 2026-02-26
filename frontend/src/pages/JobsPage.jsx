import { useState } from 'react';
import { Plus, Search, Filter, AlertTriangle } from 'lucide-react';
import { useSubscription } from '../context/SubscriptionContext';
import SubscriptionUpgradeModal from '../components/SubscriptionUpgradeModal';

const MOCK_JOBS = [
    { id: 1, job_no: 'JC-0047', vehicle: 'KA-01-MJ-1234 • Maruti Swift', complaint: 'Grinding noise when braking', state: 'REPAIR', created_at: '2026-02-25T09:15:00' },
    { id: 2, job_no: 'JC-0046', vehicle: 'KA-05-AB-9876 • Tata Nexon', complaint: 'AC not cooling', state: 'OPEN', created_at: '2026-02-25T08:30:00' },
    { id: 3, job_no: 'JC-0045', vehicle: 'MH-12-CD-5432 • Hyundai Creta', complaint: 'Engine oil change + general service', state: 'QC_PDI', created_at: '2026-02-24T14:00:00' },
    { id: 4, job_no: 'JC-0044', vehicle: 'KA-03-EF-7890 • Honda City', complaint: 'Clutch slipping at high RPM', state: 'BILLING', created_at: '2026-02-24T10:00:00' },
    { id: 5, job_no: 'JC-0043', vehicle: 'DL-01-GH-3456 • Kia Seltos', complaint: 'Suspension noise over bumps', state: 'CLOSED', created_at: '2026-02-23T16:00:00' },
    { id: 6, job_no: 'JC-0042', vehicle: 'KA-01-IJ-6543 • Toyota Innova', complaint: 'Steering vibration at 80+ kmph', state: 'CLOSED', created_at: '2026-02-23T11:00:00' },
];

const stateConfig = {
    OPEN: { dot: 'status-dot--open', badge: 'badge--info' },
    REPAIR: { dot: 'status-dot--repair', badge: 'badge--warning' },
    QC_PDI: { dot: 'status-dot--repair', badge: 'badge--accent' },
    BILLING: { dot: 'status-dot--billing', badge: 'badge--accent' },
    CLOSED: { dot: 'status-dot--closed', badge: 'badge--success' },
};

export default function JobsPage() {
    const { canPerformAction, incrementUsage, checkJobCardLimit } = useSubscription();
    const [filter, setFilter] = useState('');
    const [search, setSearch] = useState('');
    const [showCreate, setShowCreate] = useState(false);
    const [showUpgrade, setShowUpgrade] = useState(false);
    
    const jobLimitStatus = checkJobCardLimit();

    const filtered = MOCK_JOBS.filter(j => {
        if (filter && j.state !== filter) return false;
        if (search && !j.job_no.toLowerCase().includes(search.toLowerCase()) && !j.complaint.toLowerCase().includes(search.toLowerCase())) return false;
        return true;
    });

    const handleCreateClick = () => {
        const check = canPerformAction('job_card_create');
        if (!check.allowed) {
            setShowUpgrade(true);
            return;
        }
        setShowCreate(!showCreate);
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        // Simulate API call
        setTimeout(() => {
            incrementUsage('job_cards_created', 1);
            setShowCreate(false);
        }, 500);
    };

    return (
        <div className="fade-in">
            <div className="main__header">
                <h2>Job Cards</h2>
                <button 
                    className="btn btn--primary" 
                    onClick={handleCreateClick}
                    disabled={jobLimitStatus.isAtLimit}
                >
                    <Plus size={18} /> New Job Card
                </button>
            </div>
            
            {/* Limit Warning */}
            {jobLimitStatus.isNearLimit && !jobLimitStatus.isAtLimit && (
                <div style={{ 
                    background: 'rgba(234,179,8,0.1)', 
                    border: '1px solid rgba(234,179,8,0.3)',
                    borderRadius: 8,
                    padding: '12px 16px',
                    marginBottom: 16,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 8,
                }}>
                    <AlertTriangle size={16} color="var(--warning)" />
                    <span style={{ fontSize: '0.86rem', flex: 1 }}>
                        Approaching monthly job card limit ({jobLimitStatus.remaining} remaining)
                    </span>
                    <button className="btn btn--ghost btn--sm" onClick={() => setShowUpgrade(true)}>
                        Upgrade
                    </button>
                </div>
            )}
            
            {jobLimitStatus.isAtLimit && (
                <div style={{ 
                    background: 'rgba(239,68,68,0.1)', 
                    border: '1px solid rgba(239,68,68,0.3)',
                    borderRadius: 8,
                    padding: '12px 16px',
                    marginBottom: 16,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 8,
                }}>
                    <AlertTriangle size={16} color="var(--danger)" />
                    <span style={{ fontSize: '0.86rem', flex: 1, color: 'var(--danger)' }}>
                        Monthly job card limit reached. Upgrade to create more.
                    </span>
                    <button className="btn btn--primary btn--sm" onClick={() => setShowUpgrade(true)}>
                        Upgrade
                    </button>
                </div>
            )}

            {/* Create Form */}
            {showCreate && (
                <div className="card" style={{ marginBottom: 20 }}>
                    <div className="card__title">Create Job Card</div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 12, marginTop: 8 }}>
                        <div><label>Vehicle ID</label><input className="input" placeholder="Vehicle registration" /></div>
                        <div><label>Complaint</label><input className="input" placeholder="Customer complaint description" /></div>
                    </div>
                    <div style={{ display: 'flex', gap: 8, marginTop: 14 }}>
                        <button className="btn btn--primary btn--sm" onClick={handleSubmit}>Create</button>
                        <button className="btn btn--ghost btn--sm" onClick={() => setShowCreate(false)}>Cancel</button>
                    </div>
                </div>
            )}

            {/* Filters */}
            <div style={{ display: 'flex', gap: 12, marginBottom: 20 }}>
                <div style={{ flex: 1, position: 'relative' }}>
                    <Search size={16} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                    <input className="input" style={{ paddingLeft: 36 }} placeholder="Search jobs…" value={search} onChange={e => setSearch(e.target.value)} />
                </div>
                <select className="input" style={{ width: 160 }} value={filter} onChange={e => setFilter(e.target.value)}>
                    <option value="">All States</option>
                    <option value="OPEN">Open</option>
                    <option value="REPAIR">Repair</option>
                    <option value="QC_PDI">QC / PDI</option>
                    <option value="BILLING">Billing</option>
                    <option value="CLOSED">Closed</option>
                </select>
            </div>

            {/* Table */}
            <div className="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>Job No</th>
                            <th>Vehicle</th>
                            <th>Complaint</th>
                            <th>Status</th>
                            <th>Created</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filtered.map(job => {
                            const cfg = stateConfig[job.state] || stateConfig.OPEN;
                            return (
                                <tr key={job.id} style={{ cursor: 'pointer' }}>
                                    <td style={{ fontWeight: 600, color: 'var(--accent-hover)' }}>{job.job_no}</td>
                                    <td>{job.vehicle}</td>
                                    <td>{job.complaint}</td>
                                    <td>
                                        <span className={`badge ${cfg.badge}`}>
                                            <span className={`status-dot ${cfg.dot}`} />
                                            {job.state}
                                        </span>
                                    </td>
                                    <td>{new Date(job.created_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })}</td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
