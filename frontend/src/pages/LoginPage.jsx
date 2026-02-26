import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Wrench, Eye, EyeOff } from 'lucide-react';

export default function LoginPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [showPw, setShowPw] = useState(false);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            await login(username, password);
            navigate('/app');
        } catch (err) {
            setError(err.message || 'Invalid credentials');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-page">
            <div className="login-card fade-in">
                <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 16 }}>
                    <div style={{
                        width: 52, height: 52, borderRadius: 14,
                        background: 'linear-gradient(135deg, var(--accent), #8b5cf6)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        boxShadow: '0 8px 24px var(--accent-glow)'
                    }}>
                        <Wrench size={26} color="#fff" />
                    </div>
                </div>
                <h1>EKA-AI</h1>
                <p>Governed Automobile Intelligence Platform</p>

                {error && (
                    <div style={{
                        background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)',
                        borderRadius: 10, padding: '10px 14px', marginBottom: 18,
                        color: 'var(--danger)', fontSize: '0.84rem'
                    }}>
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="username">Username</label>
                        <input
                            id="username" className="input" placeholder="Enter username"
                            value={username} onChange={e => setUsername(e.target.value)}
                            autoComplete="username" required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="password">Password</label>
                        <div style={{ position: 'relative' }}>
                            <input
                                id="password" className="input" placeholder="Enter password"
                                type={showPw ? 'text' : 'password'}
                                value={password} onChange={e => setPassword(e.target.value)}
                                autoComplete="current-password" required
                            />
                            <button type="button" onClick={() => setShowPw(!showPw)} style={{
                                position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)',
                                background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer'
                            }}>
                                {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
                            </button>
                        </div>
                    </div>
                    <button
                        type="submit" className="btn btn--primary"
                        style={{ width: '100%', justifyContent: 'center', marginTop: 8 }}
                        disabled={loading}
                    >
                        {loading ? 'Signing in…' : 'Sign In'}
                    </button>
                </form>

                <p style={{ marginTop: 20, fontSize: '0.76rem', color: 'var(--text-muted)' }}>
                    Default:  admin / admin (dev mode)
                </p>
            </div>
        </div>
    );
}
