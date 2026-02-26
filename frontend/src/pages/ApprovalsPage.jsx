import { useState, useEffect } from 'react';
import { CheckCircle, XCircle, Eye, Clock, AlertTriangle, Shield, FileText, User } from 'lucide-react';
import FeatureGate from '../components/FeatureGate';

const urgencyConfig = {
    low: { color: 'var(--success)', label: 'Low' },
    normal: { color: 'var(--info)', label: 'Normal' },
    high: { color: 'var(--warning)', label: 'High' },
    critical: { color: 'var(--danger)', label: 'Critical' },
};

const statusConfig = {
    pending: { badge: 'badge--warning', label: 'Pending' },
    approved: { badge: 'badge--success', label: 'Approved' },
    rejected: { badge: 'badge--danger', label: 'Rejected' },
};

export default function ApprovalsPage() {
    const [approvals, setApprovals] = useState([]);
    const [filter, setFilter] = useState('pending');
    const [selectedApproval, setSelectedApproval] = useState(null);
    const [loading, setLoading] = useState(false);
    const [comment, setComment] = useState('');
    const [dataLoading, setDataLoading] = useState(true);

    useEffect(() => {
        fetchApprovals();
    }, []);

    const fetchApprovals = async () => {
        try {
            setDataLoading(true);
            const token = localStorage.getItem('eka_token');
            const res = await fetch('/api/v1/approvals', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                setApprovals(data);
            }
        } catch (err) {
            console.error(err);
        } finally {
            setDataLoading(false);
        }
    };

    const filtered = approvals.filter(a => filter === 'all' || a.status === filter);

    const handleApprove = async () => {
        if (!selectedApproval?.token) {
            alert('Cannot respond: token missing');
            return;
        }
        setLoading(true);
        try {
            const res = await fetch(`/api/v1/approvals/${selectedApproval.token}/respond`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ decision: 'approved' })
            });
            if (res.ok) {
                await fetchApprovals();
                setSelectedApproval(null);
            } else {
                const err = await res.json();
                alert(`Error: ${err.detail || 'Failed to approve'}`);
            }
        } catch (err) {
            console.error(err);
            alert('Network error while approving');
        } finally {
            setLoading(false);
            setComment('');
        }
    };

    const handleReject = async () => {
        if (!selectedApproval?.token) {
            alert('Cannot respond: token missing');
            return;
        }
        setLoading(true);
        try {
            const res = await fetch(`/api/v1/approvals/${selectedApproval.token}/respond`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    decision: 'rejected',
                    rejection_reason: comment || 'Rejected by manager'
                })
            });
            if (res.ok) {
                await fetchApprovals();
                setSelectedApproval(null);
            } else {
                const err = await res.json();
                alert(`Error: ${err.detail || 'Failed to reject'}`);
            }
        } catch (err) {
            console.error(err);
            alert('Network error while rejecting');
        } finally {
            setLoading(false);
            setComment('');
        }
    };

    return (
        <div className="fade-in">
            <div className="main__header">
                <h2 style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <Shield size={22} color="var(--accent)" /> Approvals
                </h2>
            </div>

            <FeatureGate feature="approvals">

                {/* Stats */}
                <div className="grid grid--4" style={{ marginBottom: 24 }}>
                    {[
                        { label: 'Pending', value: approvals.filter(a => a.status === 'pending').length, color: 'var(--warning)' },
                        { label: 'Approved Today', value: approvals.filter(a => a.status === 'approved' && a.resolved_at?.includes(new Date().toISOString().split('T')[0])).length, color: 'var(--success)' },
                        { label: 'Rejected Today', value: approvals.filter(a => a.status === 'rejected' && a.resolved_at?.includes(new Date().toISOString().split('T')[0])).length, color: 'var(--danger)' },
                        { label: 'Avg Response Time', value: '12 min', color: 'var(--accent)' },
                    ].map((stat, i) => (
                        <div className="card" key={i}>
                            <div className="card__title" style={{ fontSize: '0.78rem' }}>{stat.label}</div>
                            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: stat.color, marginTop: 4 }}>{stat.value}</div>
                        </div>
                    ))}
                </div>

                {/* Filters */}
                <div style={{ display: 'flex', gap: 10, marginBottom: 20 }}>
                    {['pending', 'approved', 'rejected', 'all'].map((f) => (
                        <button
                            key={f}
                            className={`btn ${filter === f ? 'btn--primary' : 'btn--ghost'} btn--sm`}
                            onClick={() => setFilter(f)}
                        >
                            {f.charAt(0).toUpperCase() + f.slice(1)}
                        </button>
                    ))}
                </div>

                {/* Approval Detail Modal */}
                {selectedApproval && (
                    <div
                        style={{
                            position: 'fixed',
                            top: 0, left: 0, right: 0, bottom: 0,
                            background: 'rgba(0,0,0,0.7)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            zIndex: 100,
                            padding: 20,
                        }}
                        onClick={() => setSelectedApproval(null)}
                    >
                        <div
                            className="card"
                            style={{
                                width: '100%',
                                maxWidth: 600,
                                maxHeight: '90vh',
                                overflow: 'auto',
                                position: 'relative'
                            }}
                            onClick={e => e.stopPropagation()}
                        >
                            <button
                                onClick={() => setSelectedApproval(null)}
                                style={{
                                    position: 'absolute',
                                    top: 16,
                                    right: 16,
                                    background: 'none',
                                    border: 'none',
                                    color: 'var(--text-muted)',
                                    cursor: 'pointer',
                                    fontSize: '1.2rem'
                                }}
                            >
                                ✕
                            </button>

                            <div style={{ marginBottom: 20 }}>
                                <span className={`badge ${statusConfig[selectedApproval.status]?.badge}`}>
                                    {statusConfig[selectedApproval.status]?.label}
                                </span>
                                <span
                                    className="badge"
                                    style={{
                                        marginLeft: 8,
                                        background: urgencyConfig[selectedApproval.urgency]?.color + '20',
                                        color: urgencyConfig[selectedApproval.urgency]?.color
                                    }}
                                >
                                    {urgencyConfig[selectedApproval.urgency]?.label} Priority
                                </span>
                            </div>

                            <h3 style={{ marginBottom: 12 }}>{selectedApproval.title}</h3>

                            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
                                <User size={16} color="var(--text-muted)" />
                                <span style={{ fontSize: '0.86rem', color: 'var(--text-muted)' }}>
                                    Requested by {selectedApproval.requester}
                                </span>
                                <span style={{ color: 'var(--border-glass)' }}>•</span>
                                <Clock size={14} color="var(--text-muted)" />
                                <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                                    {selectedApproval.requested_at ? new Date(selectedApproval.requested_at).toLocaleString('en-IN') : 'N/A'}
                                </span>
                            </div>

                            <div style={{
                                background: 'var(--bg-glass)',
                                padding: 16,
                                borderRadius: 10,
                                marginBottom: 20
                            }}>
                                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 8 }}>Description</div>
                                <div style={{ fontSize: '0.9rem', lineHeight: 1.5 }}>{selectedApproval.description}</div>
                            </div>

                            <div style={{
                                background: 'var(--bg-secondary)',
                                padding: 16,
                                borderRadius: 10,
                                marginBottom: 20
                            }}>
                                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 12 }}>Details</div>
                                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 10 }}>
                                    {Object.entries(selectedApproval.data || {}).map(([key, value]) => (
                                        <div key={key}>
                                            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'capitalize' }}>
                                                {key.replace(/_/g, ' ')}
                                            </div>
                                            <div style={{ fontWeight: 500, fontSize: '0.88rem' }}>{value}</div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {selectedApproval.status === 'pending' ? (
                                <>
                                    <div style={{ marginBottom: 16 }}>
                                        <label>Comment (optional)</label>
                                        <textarea
                                            className="input"
                                            rows={3}
                                            placeholder="Add a note about this decision..."
                                            value={comment}
                                            onChange={e => setComment(e.target.value)}
                                            style={{ resize: 'none' }}
                                        />
                                    </div>
                                    <div style={{ display: 'flex', gap: 10 }}>
                                        <button
                                            className="btn btn--primary"
                                            onClick={handleApprove}
                                            disabled={loading}
                                            style={{ flex: 1 }}
                                        >
                                            <CheckCircle size={18} style={{ marginRight: 6 }} />
                                            Approve
                                        </button>
                                        <button
                                            className="btn btn--ghost"
                                            onClick={handleReject}
                                            disabled={loading}
                                            style={{ flex: 1, borderColor: 'var(--danger)', color: 'var(--danger)' }}
                                        >
                                            <XCircle size={18} style={{ marginRight: 6 }} />
                                            Reject
                                        </button>
                                    </div>
                                </>
                            ) : (
                                <div style={{
                                    background: selectedApproval.status === 'approved' ? 'rgba(34,197,94,0.1)' : 'rgba(239,68,68,0.1)',
                                    padding: 16,
                                    borderRadius: 10,
                                    border: `1px solid ${selectedApproval.status === 'approved' ? 'rgba(34,197,94,0.3)' : 'rgba(239,68,68,0.3)'}`,
                                }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                                        {selectedApproval.status === 'approved' ?
                                            <CheckCircle size={18} color="var(--success)" /> :
                                            <XCircle size={18} color="var(--danger)" />
                                        }
                                        <span style={{ fontWeight: 600, color: selectedApproval.status === 'approved' ? 'var(--success)' : 'var(--danger)' }}>
                                            {selectedApproval.status === 'approved' ? 'Approved' : 'Rejected'} by {selectedApproval.resolved_by}
                                        </span>
                                    </div>
                                    <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                                        {selectedApproval.resolved_at ? new Date(selectedApproval.resolved_at).toLocaleString('en-IN') : 'N/A'}
                                    </div>
                                    {selectedApproval.rejection_reason && (
                                        <div style={{ marginTop: 8, fontSize: '0.86rem' }}>
                                            Reason: {selectedApproval.rejection_reason}
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Approval List */}
                {dataLoading ? (
                    <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-muted)' }}>
                        Loading approvals...
                    </div>
                ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                        {filtered.map(approval => {
                            const cfg = statusConfig[approval.status];
                            const urg = urgencyConfig[approval.urgency] || urgencyConfig['normal'];
                            return (
                                <div
                                    key={approval.id}
                                    className="card"
                                    style={{
                                        cursor: 'pointer',
                                        borderLeft: `4px solid ${approval.status === 'pending' ? urg.color : cfg?.color}`,
                                    }}
                                    onClick={() => setSelectedApproval(approval)}
                                >
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                        <div style={{ flex: 1 }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
                                                <h4 style={{ margin: 0, fontSize: '0.95rem' }}>{approval.title}</h4>
                                                <span className={`badge ${cfg?.badge}`} style={{ fontSize: '0.7rem' }}>
                                                    {cfg?.label}
                                                </span>
                                                {approval.status === 'pending' && (
                                                    <span
                                                        className="badge"
                                                        style={{
                                                            fontSize: '0.7rem',
                                                            background: urg.color + '20',
                                                            color: urg.color
                                                        }}
                                                    >
                                                        {urg.label}
                                                    </span>
                                                )}
                                            </div>
                                            <p style={{
                                                margin: '0 0 8px 0',
                                                fontSize: '0.84rem',
                                                color: 'var(--text-secondary)',
                                                lineHeight: 1.4
                                            }}>
                                                {approval.description}
                                            </p>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: 12, fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                                                <span>{approval.requester}</span>
                                                <span>•</span>
                                                <span>{approval.requested_at ? new Date(approval.requested_at).toLocaleString('en-IN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : 'N/A'}</span>
                                            </div>
                                        </div>
                                        <button className="btn btn--ghost btn--sm">
                                            <Eye size={16} />
                                        </button>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}

                {!dataLoading && filtered.length === 0 && (
                    <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-muted)' }}>
                        <CheckCircle size={48} style={{ opacity: 0.3, marginBottom: 16 }} />
                        <div>No {filter !== 'all' ? filter : ''} approvals found</div>
                    </div>
                )}
            </FeatureGate>
        </div>
    );
}
