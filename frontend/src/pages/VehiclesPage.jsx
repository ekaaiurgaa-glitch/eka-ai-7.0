import { useState, useMemo } from 'react';
import { Plus, Search, Filter } from 'lucide-react';

const MOCK_VEHICLES = [
    { id: 1, plate_number: 'KA-01-MJ-1234', make: 'Maruti', model: 'Swift', variant: 'VXI', year: 2019, fuel_type: 'petrol' },
    { id: 2, plate_number: 'KA-05-AB-9876', make: 'Tata', model: 'Nexon', variant: 'XZ+', year: 2021, fuel_type: 'diesel' },
    { id: 3, plate_number: 'MH-12-CD-5432', make: 'Hyundai', model: 'Creta', variant: 'SX', year: 2022, fuel_type: 'petrol' },
    { id: 4, plate_number: 'KA-03-EF-7890', make: 'Honda', model: 'City', variant: 'ZX', year: 2020, fuel_type: 'petrol' },
    { id: 5, plate_number: 'DL-01-GH-3456', make: 'Kia', model: 'Seltos', variant: 'HTX', year: 2023, fuel_type: 'diesel' },
];

export default function VehiclesPage() {
    const [showCreate, setShowCreate] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const [fuelFilter, setFuelFilter] = useState('All');
    const [form, setForm] = useState({ plate_number: '', make: '', model: '', variant: '', year: 2024, fuel_type: 'Petrol', vin: '' });

    const filteredVehicles = useMemo(() => {
        return MOCK_VEHICLES.filter(v => {
            const matchesSearch =
                v.plate_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
                v.make.toLowerCase().includes(searchTerm.toLowerCase()) ||
                v.model.toLowerCase().includes(searchTerm.toLowerCase());

            const matchesFuel = fuelFilter === 'All' || v.fuel_type.toLowerCase() === fuelFilter.toLowerCase();

            return matchesSearch && matchesFuel;
        });
    }, [searchTerm, fuelFilter]);

    return (
        <div className="fade-in">
            <div className="main__header">
                <h2>Vehicles</h2>
                <button className="btn btn--primary" onClick={() => setShowCreate(!showCreate)}>
                    <Plus size={18} /> Register Vehicle
                </button>
            </div>

            <div className="card" style={{ marginBottom: 20, display: 'flex', gap: 16, alignItems: 'center' }}>
                <div style={{ position: 'relative', flex: 1 }}>
                    <Search size={18} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                    <input
                        className="input"
                        style={{ paddingLeft: 40 }}
                        placeholder="Search by plate, make or model..."
                        value={searchTerm}
                        onChange={e => setSearchTerm(e.target.value)}
                    />
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <Filter size={18} style={{ color: 'var(--text-muted)' }} />
                    <select
                        className="input"
                        style={{ width: 150 }}
                        value={fuelFilter}
                        onChange={e => setFuelFilter(e.target.value)}
                    >
                        <option>All</option>
                        <option>Petrol</option>
                        <option>Diesel</option>
                        <option>Electric</option>
                        <option>Hybrid</option>
                    </select>
                </div>
            </div>

            {showCreate && (
                <div className="card" style={{ marginBottom: 20 }}>
                    <div className="card__title">Register New Vehicle</div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, marginTop: 8 }}>
                        <div><label>Plate Number</label><input className="input" placeholder="KA-01-XX-1234" value={form.plate_number} onChange={e => setForm({ ...form, plate_number: e.target.value })} /></div>
                        <div><label>Make</label><input className="input" placeholder="e.g. Maruti" value={form.make} onChange={e => setForm({ ...form, make: e.target.value })} /></div>
                        <div><label>Model</label><input className="input" placeholder="e.g. Swift" value={form.model} onChange={e => setForm({ ...form, model: e.target.value })} /></div>
                        <div><label>Variant</label><input className="input" placeholder="e.g. VXI" value={form.variant} onChange={e => setForm({ ...form, variant: e.target.value })} /></div>
                        <div><label>Year</label><input className="input" type="number" placeholder="2024" value={form.year} onChange={e => setForm({ ...form, year: e.target.value })} /></div>
                        <div><label>Fuel Type</label>
                            <select className="input" value={form.fuel_type} onChange={e => setForm({ ...form, fuel_type: e.target.value })}>
                                <option>Petrol</option><option>Diesel</option><option>Electric</option><option>Hybrid</option>
                            </select>
                        </div>
                        <div style={{ gridColumn: 'span 3' }}><label>VIN (optional)</label><input className="input" placeholder="Vehicle Identification Number" value={form.vin} onChange={e => setForm({ ...form, vin: e.target.value })} /></div>
                    </div>
                    <div style={{ display: 'flex', gap: 8, marginTop: 14 }}>
                        <button className="btn btn--primary btn--sm">Register</button>
                        <button className="btn btn--ghost btn--sm" onClick={() => setShowCreate(false)}>Cancel</button>
                    </div>
                </div>
            )}

            <div className="grid grid--3">
                {filteredVehicles.map(v => (
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
            {filteredVehicles.length === 0 && (
                <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
                    No vehicles found matching your criteria.
                </div>
            )}
        </div>
    );
}
