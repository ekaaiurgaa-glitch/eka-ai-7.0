import { useState } from 'react';
import { Calculator, Shield, AlertTriangle } from 'lucide-react';
import FeatureGate from '../components/FeatureGate';

export default function MGPage() {
    const [form, setForm] = useState({
        make: 'Tata', model: 'Nexon', variant: 'XZ+', year: 2021, fuel_type: 'diesel',
        city: 'Mumbai', monthly_km: 2500, warranty_status: 'out_of_warranty', usage_type: 'commercial',
    });
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const calculate = async () => {
        setLoading(true); setError('');
        try {
            const token = localStorage.getItem('eka_token');
            const res = await fetch('/api/v1/mg/calculate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify(form),
            });
            if (!res.ok) throw new Error((await res.json()).detail || 'Calculation failed');
            setResult(await res.json());
        } catch (e) { setError(e.message); }
        finally { setLoading(false); }
    };

    const riskColor = result?.risk_level === 'high' ? 'var(--danger)' : result?.risk_level === 'medium' ? 'var(--warning)' : 'var(--success)';

    return (
        <div className="fade-in">
            <div className="main__header">
                <h2 style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <Shield size={22} color="var(--accent)" /> MG Engine
                </h2>
            </div>

            <FeatureGate feature="mg_calculator">

                <div className="grid grid--2">
                    {/* Input Form */}
                    <div className="card">
                        <div className="card__title">Vehicle & Usage Parameters</div>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginTop: 8 }}>
                            <div><label>Make</label><input className="input" value={form.make} onChange={e => setForm({ ...form, make: e.target.value })} /></div>
                            <div><label>Model</label><input className="input" value={form.model} onChange={e => setForm({ ...form, model: e.target.value })} /></div>
                            <div><label>Variant</label><input className="input" placeholder="e.g. VXI" value={form.variant} onChange={e => setForm({ ...form, variant: e.target.value })} /></div>
                            <div><label>Year</label><input className="input" type="number" value={form.year} onChange={e => setForm({ ...form, year: +e.target.value })} /></div>
                            <div><label>Fuel Type</label>
                                <select className="input" value={form.fuel_type} onChange={e => setForm({ ...form, fuel_type: e.target.value })}>
                                    <option value="petrol">Petrol</option><option value="diesel">Diesel</option>
                                    <option value="electric">Electric</option><option value="hybrid">Hybrid</option>
                                </select>
                            </div>
                            <div><label>City</label><input className="input" value={form.city} onChange={e => setForm({ ...form, city: e.target.value })} /></div>
                            <div><label>Monthly KM</label><input className="input" type="number" value={form.monthly_km} onChange={e => setForm({ ...form, monthly_km: +e.target.value })} /></div>
                            <div><label>Warranty</label>
                                <select className="input" value={form.warranty_status} onChange={e => setForm({ ...form, warranty_status: e.target.value })}>
                                    <option value="under_warranty">Under Warranty</option>
                                    <option value="out_of_warranty">Out of Warranty</option>
                                </select>
                            </div>
                            <div><label>Usage Type</label>
                                <select className="input" value={form.usage_type} onChange={e => setForm({ ...form, usage_type: e.target.value })}>
                                    <option value="personal">Personal</option>
                                    <option value="commercial">Commercial</option>
                                </select>
                            </div>
                        </div>

                        {error && <div style={{ marginTop: 12, color: 'var(--danger)', fontSize: '0.84rem' }}>⚠️ {error}</div>}

                        <button className="btn btn--primary" style={{ marginTop: 18, width: '100%', justifyContent: 'center' }} onClick={calculate} disabled={loading}>
                            <Calculator size={18} /> {loading ? 'Calculating…' : 'Calculate MG'}
                        </button>
                    </div>

                    {/* Result */}
                    <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: result ? 'flex-start' : 'center', alignItems: result ? 'stretch' : 'center' }}>
                        {!result ? (
                            <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                                <Shield size={48} style={{ opacity: 0.2, marginBottom: 12 }} />
                                <p>Configure parameters and click Calculate</p>
                            </div>
                        ) : (
                            <>
                                <div className="card__title">MG Calculation Result</div>
                                <div style={{ textAlign: 'center', margin: '16px 0' }}>
                                    <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: 4 }}>Monthly MG Fee</div>
                                    <div style={{ fontSize: '2.4rem', fontWeight: 800, color: 'var(--accent-hover)' }}>₹{result.monthly_mg.toLocaleString('en-IN')}</div>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'center', gap: 12, marginBottom: 20 }}>
                                    <span className="badge" style={{ background: riskColor + '20', color: riskColor, borderColor: riskColor + '40' }}>
                                        Risk: {result.risk_level.toUpperCase()}
                                    </span>
                                    <span className="badge badge--accent">Buffer: {result.risk_buffer_pct}%</span>
                                </div>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                                    {[
                                        ['Annual Parts', `₹${result.annual_parts.toLocaleString('en-IN')}`],
                                        ['Annual Labor', `₹${result.annual_labor.toLocaleString('en-IN')}`],
                                        ['City Multiplier', `${result.city_adj}x`],
                                        ['Risk Multiplier', `${result.risk_adj}x`],
                                        ['Final Annual Cost', `₹${result.final_annual_cost.toLocaleString('en-IN')}`],
                                    ].map(([label, val], i) => (
                                        <div key={i} style={{ background: 'var(--bg-glass)', padding: '10px 12px', borderRadius: 10 }}>
                                            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{label}</div>
                                            <div style={{ fontWeight: 600, marginTop: 2 }}>{val}</div>
                                        </div>
                                    ))}
                                </div>
                            </>
                        )}
                    </div>
                </div>
            </FeatureGate>
        </div>
    );
}
