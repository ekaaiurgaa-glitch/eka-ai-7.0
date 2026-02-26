import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import JobCardStateTransition from '../components/JobCardStateTransition';
import EstimateForm from '../components/EstimateForm';
import InvoiceView from '../components/InvoiceView';

export default function JobCardDetailPage() {
    const { jobId } = useParams();
    const navigate = useNavigate();
    const [job, setJob] = useState(null);
    const [invoice, setInvoice] = useState(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('details');

    const fetchJobDetails = useCallback(async () => {
        try {
            const token = localStorage.getItem('eka_token');
            const res = await fetch(`/api/v1/job-cards/${jobId}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (!res.ok) throw new Error('Failed to fetch job');
            const data = await res.json();
            setJob(data);

            // Fetch invoice if in appropriate state
            if (['INVOICED', 'PAID', 'CLOSED'].includes(data.state)) {
                const invRes = await fetch(`/api/v1/invoices/job/${jobId}`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (invRes.ok) {
                    setInvoice(await invRes.json());
                }
            }
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    }, [jobId]);

    useEffect(() => {
        fetchJobDetails();
    }, [fetchJobDetails]);

    const handleMarkPaid = async (invoiceId) => {
        try {
            const token = localStorage.getItem('eka_token');
            const res = await fetch(`/api/v1/invoices/${invoiceId}/pay`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                // Also transition job card to PAID if it's currently INVOICED
                if (job.state === 'INVOICED') {
                    await fetch(`/api/v1/job-cards/${jobId}/transition`, {
                        method: 'PATCH',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`
                        },
                        body: JSON.stringify({ new_state: 'PAID' })
                    });
                }
                fetchJobDetails();
            }
        } catch (err) {
            alert('Failed to mark paid: ' + err.message);
        }
    };

    if (loading) return <div style={{ padding: 20, color: 'var(--text-muted)' }}>Loading job details...</div>;
    if (!job) return <div style={{ padding: 20 }}>Job card not found</div>;

    const tabs = [
        { id: 'details', label: 'Details' },
        { id: 'transition', label: 'Status' },
        { id: 'estimate', label: 'Estimate' },
    ];

    if (['INVOICED', 'PAID', 'CLOSED'].includes(job.state)) {
        tabs.push({ id: 'invoice', label: 'Invoice' });
    }

    tabs.push({ id: 'history', label: 'History' });

    return (
        <div className="fade-in">
            <div className="main__header">
                <h2>Job Card: {job.job_no || `#${job.id}`}</h2>
                <button className="btn btn--ghost" onClick={() => navigate('/app/jobs')}>
                    ← Back to List
                </button>
            </div>

            {/* Tabs */}
            <div style={{ display: 'flex', gap: '8px', marginBottom: '24px', overflowX: 'auto', paddingBottom: '8px' }}>
                {tabs.map(tab => (
                    <button
                        key={tab.id}
                        className={`btn ${activeTab === tab.id ? 'btn--primary' : 'btn--ghost'}`}
                        onClick={() => setActiveTab(tab.id)}
                        style={{ whiteSpace: 'nowrap' }}
                    >
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Tab Content */}
            {activeTab === 'details' && (
                <div className="card">
                    {/* ... (rest of details content) ... */}
                    <div className="card__title">General Information</div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '24px', marginTop: 16 }}>
                        <div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Job Number</div>
                            <div style={{ fontWeight: 600, fontSize: '1.1rem' }}>{job.job_no || 'N/A'}</div>
                        </div>
                        <div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Status</div>
                            <div style={{ fontWeight: 600, fontSize: '1.1rem' }}>{job.state}</div>
                        </div>
                        <div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Vehicle ID</div>
                            <div style={{ fontWeight: 600, fontSize: '1.1rem' }}>{job.vehicle_id}</div>
                        </div>
                        <div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Created At</div>
                            <div style={{ fontWeight: 600, fontSize: '1.1rem' }}>{new Date(job.created_at).toLocaleString()}</div>
                        </div>
                    </div>

                    <div style={{ marginTop: 24, borderTop: '1px solid var(--border-glass)', paddingTop: 16 }}>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 8 }}>Complaint</div>
                        <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>{job.complaint || 'No complaint details provided.'}</div>
                    </div>
                </div>
            )}

            {activeTab === 'transition' && (
                <JobCardStateTransition
                    jobId={jobId}
                    currentState={job.state}
                    onTransition={(updatedJob) => {
                        setJob(updatedJob);
                        fetchJobDetails();
                    }}
                />
            )}

            {activeTab === 'estimate' && (
                <EstimateForm
                    jobId={jobId}
                    onEstimateCreated={() => {
                        fetchJobDetails();
                        setActiveTab('details');
                    }}
                />
            )}

            {activeTab === 'invoice' && (
                <InvoiceView
                    invoice={invoice}
                    onMarkPaid={handleMarkPaid}
                />
            )}

            {activeTab === 'history' && (
                <div className="card">
                    <div className="card__title">State History</div>
                    <p style={{ color: 'var(--text-muted)', marginTop: 12 }}>
                        State transition history would be displayed here from audit logs.
                    </p>
                    <div style={{ marginTop: 20 }}>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                            <div style={{ display: 'flex', gap: 12 }}>
                                <div style={{ width: 12, height: 12, borderRadius: '50%', background: 'var(--accent)', marginTop: 6 }} />
                                <div>
                                    <div style={{ fontWeight: 600 }}>Created</div>
                                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{new Date(job.created_at).toLocaleString()}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

