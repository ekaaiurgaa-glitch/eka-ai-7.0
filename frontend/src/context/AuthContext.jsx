import { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [token, setToken] = useState(() => localStorage.getItem('eka_token'));
    const [user, setUser] = useState(null);

    useEffect(() => {
        if (token) {
            try {
                const payload = JSON.parse(atob(token.split('.')[1]));
                setUser({ sub: payload.sub, tenant_id: payload.tenant_id, role: payload.role, permissions: payload.permissions });
            } catch { setUser(null); }
        } else {
            setUser(null);
        }
    }, [token]);

    const login = async (username, password) => {
        const res = await api.login(username, password);
        if (res.access_token) {
            localStorage.setItem('eka_token', res.access_token);
            setToken(res.access_token);
            return true;
        }
        throw new Error(res.detail || 'Login failed');
    };

    const logout = () => {
        localStorage.removeItem('eka_token');
        setToken(null);
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ token, user, login, logout, isAuthenticated: !!token }}>
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => useContext(AuthContext);
