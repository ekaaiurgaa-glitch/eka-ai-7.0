const BASE = '/api/v1';

async function request(method, path, body = null) {
  const token = localStorage.getItem('eka_token');
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (res.status === 401) {
    localStorage.removeItem('eka_token');
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'API Error');
  }

  return res.json();
}

export const api = {
  // Auth
  login: (email, password) => {
    return fetch(`${BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    }).then(async (r) => {
      const text = await r.text();
      if (!text) {
        throw new Error('Unable to connect to EKA services. Please try again in a few moments.');
      }
      try {
        return JSON.parse(text);
      } catch {
        throw new Error('An unexpected error occurred. Please try again.');
      }
    });
  },

  // Chat
  chatQuery: (query, vehicle) => request('POST', '/chat/query', { query, vehicle }),

  // Jobs
  listJobs: (state) => request('GET', `/job-cards${state ? `?state=${state}` : ''}`),
  getJob: (id) => request('GET', `/job-cards/${id}`),
  createJob: (data) => request('POST', '/job-cards', data),
  transitionJob: (id, newState) => request('PATCH', `/job-cards/${id}/transition`, { new_state: newState }),

  // Vehicles
  listVehicles: () => request('GET', '/vehicles'),
  createVehicle: (data) => request('POST', '/vehicles', data),

  // MG
  calculateMG: (data) => request('POST', '/mg/calculate', data),

  // Dashboard
  workshopDashboard: () => request('GET', '/dashboards/workshop'),

  // Health
  health: () => fetch('/health').then(r => r.json()),
};
