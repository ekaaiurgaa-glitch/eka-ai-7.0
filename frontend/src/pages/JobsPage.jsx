import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Search, Filter, AlertTriangle } from 'lucide-react';
import { useSubscription } from '../context';
import SubscriptionUpgradeModal from '../components/SubscriptionUpgradeModal';

const stateConfig = {
    OPEN: { dot: 'status-dot--open', badge: 'badge--info' },
    DIAGNOSIS: { dot: 'status-dot--repair', badge: 'badge--warning' },
    REPAIR: { dot: 'status-dot--repair', badge: 'badge--warning' },
    QC_PDI: { dot: 'status-dot--repair', badge: 'badge--accent' },
    ESTIMATE_PENDING: { dot: 'status-dot--repair', badge: 'badge--warning' },
    APPROVAL_PENDING: { dot: 'status-dot--repair', badge: 'badge--warning' },
    APPROVED: { dot: 'status-dot--repair', badge: 'badge--success' },
    READY: { dot: 'status-dot--repair', badge: 'badge--success' },
    BILLING: { dot: 'status-dot--billing', badge: 'badge--accent' },
    INVOICED: { dot: 'status-dot--billing', badge: 'badge--accent' },
    PAID: { dot: 'status-dot--closed', badge: 'badge--success' },
    CLOSED: { dot: 'status-dot--closed', badge: 'badge--success' },
    CANCELLED: { dot: 'status-dot--closed', badge: 'badge--danger' },
    REJECTED: { dot: 'status-dot--closed', badge: 'badge--danger' },
};

export default function JobsPage() {
    const navigate = useNavigate();
    const { canPerformAction, incrementUsage, checkJobCardLimit } = useSubscription();
    const [jobs, setJobs] = useState([]);
    const [filter, setFilter] = useState('');
    const [search, setSearch] = useState('');
    const [showCreate, setShowCreate] = useState(false);
    const [showUpgrade, setShowUpgrade] = useState(false);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);

    const fetchJobs = useCallback(async () => {
        try {
            setLoading(true);
            const token = localStorage.getItem('eka_token');
            const url = filter ? `/api/v1/job-cards?state=${filter}` : '/api/v1/job-cards';
            const res = await fetch(url, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (!res.ok) throw new Error('Failed to fetch jobs');
            const data = await res.json();
            setJobs(data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    }, [filter]);

    useEffect(() => {
        fetchJobs();
    }, [fetchJobs]);

    const jobLimitStatus = checkJobCardLimit();

    const filtered = jobs.filter(j => {
        const jobNo = j.job_no || `#${j.id}`;
        if (search && !jobNo.toLowerCase().includes(search.toLowerCase()) &&
            !(j.complaint || '').toLowerCase().includes(search.toLowerCase())) return false;
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

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSubmitting(true);
        const formData = new FormData(e.currentTarget);
        const vehicle_id = formData.get('vehicleId');
        const complaint = formData.get('complaint');

        try {
            const token = localStorage.getItem('eka_token');
            const res = await fetch('/api/v1/job-cards', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ vehicle_id, complaint }),
            });

            if (!res.ok) throw new Error('Failed to create job card');

            incrementUsage('job_cards_created', 1);
            setShowCreate(false);
            fetchJobs();
        } catch (err) {
            alert(err.message);
        } finally {
            setSubmitting(false);
        }
    };

    if (loading && jobs.length === 0) return <div style={{ padding: 20, color: 'var(--text-muted)' }}>Loading job cards...</div>;

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
                    <form onSubmit={handleSubmit}>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 12, marginTop: 8 }}>
                            <div><label>Vehicle ID</label><input className="input" name="vehicleId" placeholder="Vehicle reg e.g. KA01MJ1234" required /></div>
                            <div><label>Complaint</label><input className="input" name="complaint" placeholder="Customer complaint description" required /></div>
                        </div>
                        <div style={{ display: 'flex', gap: 8, marginTop: 14 }}>
                            <button className="btn btn--primary btn--sm" type="submit" disabled={submitting}>
                                {submitting ? 'Creating...' : 'Create'}
                            </button>
                            <button className="btn btn--ghost btn--sm" type="button" onClick={() => setShowCreate(false)}>Cancel</button>
                        </div>
                    </form>
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
                    <option value="DIAGNOSIS">Diagnosis</option>
                    <option value="ESTIMATE_PENDING">Estimate Pending</option>
                    <option value="APPROVAL_PENDING">Approval Pending</option>
                    <option value="APPROVED">Approved</option>
                    <option value="REPAIR">Repair</option>
                    <option value="QC_PDI">QC / PDI</option>
                    <option value="READY">Ready</option>
                    <option value="INVOICED">Invoiced</option>
                    <option value="PAID">Paid</option>
                    <option value="CLOSED">Closed</option>
                    <option value="CANCELLED">Cancelled</option>
                    <option value="REJECTED">Rejected</option>
                </select>
            </div>

            {/* Table */}
            <div className="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>Job No</th>
                            <th>Vehicle ID</th>
                            <th>Complaint</th>
                            <th>Status</th>
                            <th>Created</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filtered.length === 0 ? (
                            <tr><td colSpan="5" style={{ textAlign: 'center', color: 'var(--text-muted)', padding: 20 }}>No job cards found</td></tr>
                        ) : filtered.map(job => {
                            const cfg = stateConfig[job.state] || stateConfig.OPEN;
                            return (
                                <tr key={job.id} style={{ cursor: 'pointer' }} onClick={() => navigate(`/app/jobs/${job.id}`)}>
                                    <td style={{ fontWeight: 600, color: 'var(--accent-hover)' }}>{job.job_no || `#${job.id}`}</td>
                                    <td>{job.vehicle_id}</td>
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

            {showUpgrade && (
                <SubscriptionUpgradeModal
                    isOpen={showUpgrade}
                    onClose={() => setShowUpgrade(false)}
                />
            )}
        </div>
    );
}
