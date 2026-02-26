import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

/* global process */

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: process.env.VITE_BACKEND_URL || 'http://localhost:8001',
        changeOrigin: true,
        configure: (_proxy) => {
          _proxy.on('error', (err) => {
            console.error('Proxy error:', err.message);
          });
        },
      },
      '/token': {
        target: process.env.VITE_BACKEND_URL || 'http://localhost:8001',
        changeOrigin: true,
      },
      '/health': {
        target: process.env.VITE_BACKEND_URL || 'http://localhost:8001',
        changeOrigin: true,
      }
    }
  }
})
