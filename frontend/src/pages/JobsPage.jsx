import { useState } from 'react';
import { Plus, Search, Filter } from 'lucide-react';

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
    const [filter, setFilter] = useState('');
    const [search, setSearch] = useState('');
    const [showCreate, setShowCreate] = useState(false);

    const filtered = MOCK_JOBS.filter(j => {
        if (filter && j.state !== filter) return false;
        if (search && !j.job_no.toLowerCase().includes(search.toLowerCase()) && !j.complaint.toLowerCase().includes(search.toLowerCase())) return false;
        return true;
    });

    return (
        <div className="fade-in">
            <div className="main__header">
                <h2>Job Cards</h2>
                <button className="btn btn--primary" onClick={() => setShowCreate(!showCreate)}>
                    <Plus size={18} /> New Job Card
                </button>
            </div>

            {/* Create Form */}
            {showCreate && (
                <div className="card" style={{ marginBottom: 20 }}>
                    <div className="card__title">Create Job Card</div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 12, marginTop: 8 }}>
                        <div><label>Vehicle ID</label><input className="input" placeholder="Vehicle registration" /></div>
                        <div><label>Complaint</label><input className="input" placeholder="Customer complaint description" /></div>
                    </div>
                    <div style={{ display: 'flex', gap: 8, marginTop: 14 }}>
                        <button className="btn btn--primary btn--sm">Create</button>
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
