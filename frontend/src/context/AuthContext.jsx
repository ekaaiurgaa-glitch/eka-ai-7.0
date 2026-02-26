import { useState, useMemo } from 'react';
import { api } from '../api';
import { AuthContext } from './AuthContextObject';

export function AuthProvider({ children }) {
    const [token, setToken] = useState(() => localStorage.getItem('eka_token'));

    const user = useMemo(() => {
        if (!token) return null;
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            return { sub: payload.sub, tenant_id: payload.tenant_id, role: payload.role, permissions: payload.permissions };
        } catch { return null; }
    }, [token]);

    const login = async (username, password) => {
        const res = await api.login(username, password);
        if (res.access_token) {
            localStorage.setItem('eka_token', res.access_token);
            setToken(res.access_token);
            return true;
        }
        throw new Error(res.detail || res.message || 'Login failed');
    };

    const logout = () => {
        localStorage.removeItem('eka_token');
        setToken(null);
    };

    return (
        <AuthContext.Provider value={{ token, user, login, logout, isAuthenticated: !!token }}>
            {children}
        </AuthContext.Provider>
    );
}
