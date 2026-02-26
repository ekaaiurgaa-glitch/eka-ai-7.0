import { useState } from 'react';
import { Plus } from 'lucide-react';

const MOCK_VEHICLES = [
    { id: 1, plate_number: 'KA-01-MJ-1234', make: 'Maruti', model: 'Swift', variant: 'VXI', year: 2019, fuel_type: 'petrol' },
    { id: 2, plate_number: 'KA-05-AB-9876', make: 'Tata', model: 'Nexon', variant: 'XZ+', year: 2021, fuel_type: 'diesel' },
    { id: 3, plate_number: 'MH-12-CD-5432', make: 'Hyundai', model: 'Creta', variant: 'SX', year: 2022, fuel_type: 'petrol' },
    { id: 4, plate_number: 'KA-03-EF-7890', make: 'Honda', model: 'City', variant: 'ZX', year: 2020, fuel_type: 'petrol' },
    { id: 5, plate_number: 'DL-01-GH-3456', make: 'Kia', model: 'Seltos', variant: 'HTX', year: 2023, fuel_type: 'diesel' },
];

export default function VehiclesPage() {
    const [showCreate, setShowCreate] = useState(false);
    const [form, setForm] = useState({ plate_number: '', make: '', model: '', variant: '', year: 2024, fuel_type: 'Petrol', vin: '' });

    return (
        <div className="fade-in">
            <div className="main__header">
                <h2>Vehicles</h2>
                <button className="btn btn--primary" onClick={() => setShowCreate(!showCreate)}>
                    <Plus size={18} /> Register Vehicle
                </button>
            </div>

            {showCreate && (
                <div className="card" style={{ marginBottom: 20 }}>
                    <div className="card__title">Register New Vehicle</div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, marginTop: 8 }}>
                        <div><label>Plate Number</label><input className="input" placeholder="KA-01-XX-1234" value={form.plate_number} onChange={e => setForm({...form, plate_number: e.target.value})} /></div>
                        <div><label>Make</label><input className="input" placeholder="e.g. Maruti" value={form.make} onChange={e => setForm({...form, make: e.target.value})} /></div>
                        <div><label>Model</label><input className="input" placeholder="e.g. Swift" value={form.model} onChange={e => setForm({...form, model: e.target.value})} /></div>
                        <div><label>Variant</label><input className="input" placeholder="e.g. VXI" value={form.variant} onChange={e => setForm({...form, variant: e.target.value})} /></div>
                        <div><label>Year</label><input className="input" type="number" placeholder="2024" value={form.year} onChange={e => setForm({...form, year: e.target.value})} /></div>
                        <div><label>Fuel Type</label>
                            <select className="input" value={form.fuel_type} onChange={e => setForm({...form, fuel_type: e.target.value})}>
                                <option>Petrol</option><option>Diesel</option><option>Electric</option><option>Hybrid</option>
                            </select>
                        </div>
                        <div style={{ gridColumn: 'span 3' }}><label>VIN (optional)</label><input className="input" placeholder="Vehicle Identification Number" value={form.vin} onChange={e => setForm({...form, vin: e.target.value})} /></div>
                    </div>
                    <div style={{ display: 'flex', gap: 8, marginTop: 14 }}>
                        <button className="btn btn--primary btn--sm">Register</button>
                        <button className="btn btn--ghost btn--sm" onClick={() => setShowCreate(false)}>Cancel</button>
                    </div>
                </div>
            )}

            <div className="grid grid--3">
                {MOCK_VEHICLES.map(v => (
                    <div className="card" key={v.id} style={{ cursor: 'pointer' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                            <span style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--accent-hover)' }}>{v.plate_number}</span>
                            <span className="badge badge--info">{v.fuel_type}</span>
                        </div>
                        <div style={{ fontSize: '1.05rem', fontWeight: 600 }}>{v.make} {v.model} <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>({v.variant})</span></div>
                        <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: 4 }}>Year: {v.year}</div>
                    </div>
                ))}
            </div>
        </div>
    );
}
