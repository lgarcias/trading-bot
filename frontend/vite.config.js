import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    historyApiFallback: true, // Permite SPA fallback en desarrollo
    proxy: {
      '/api': 'http://localhost:8000', // Solo proxyea las rutas de API
      // añade aquí más rutas si tu backend expone otras
    }
  }
})
