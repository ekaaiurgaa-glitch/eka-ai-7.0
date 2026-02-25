import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
    LayoutDashboard, MessageSquare, ClipboardList, Car,
    Shield, Settings, LogOut, Wrench,
} from 'lucide-react';

const navItems = [
    { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/chat', icon: MessageSquare, label: 'EKA Intelligence' },
    { to: '/jobs', icon: ClipboardList, label: 'Job Cards' },
    { to: '/vehicles', icon: Car, label: 'Vehicles' },
    { to: '/mg', icon: Shield, label: 'MG Engine' },
];

export default function Sidebar() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => { logout(); navigate('/login'); };

    return (
        <aside className="sidebar">
            <div className="sidebar__logo">
                <Wrench size={22} color="var(--accent)" />
                <div>
                    <h1>EKA-AI</h1>
                    <span>Governed Intelligence</span>
                </div>
            </div>

            <nav className="sidebar__nav">
                {navItems.map(({ to, icon: Icon, label }) => (
                    <NavLink
                        key={to}
                        to={to}
                        end={to === '/'}
                        className={({ isActive }) =>
                            `sidebar__link ${isActive ? 'sidebar__link--active' : ''}`
                        }
                    >
                        <Icon size={18} />
                        {label}
                    </NavLink>
                ))}
            </nav>

            <div style={{ borderTop: '1px solid var(--border-glass)', paddingTop: 16, marginTop: 8 }}>
                <div style={{ padding: '8px 12px', marginBottom: 8 }}>
                    <div style={{ fontSize: '0.82rem', fontWeight: 600 }}>{user?.sub || 'User'}</div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{user?.role || 'owner'}</div>
                </div>
                <button className="sidebar__link" onClick={handleLogout} style={{ border: 'none', width: '100%', cursor: 'pointer', background: 'none' }}>
                    <LogOut size={18} />
                    Sign Out
                </button>
            </div>
        </aside>
    );
}
