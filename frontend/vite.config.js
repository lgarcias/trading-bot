import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/history': 'http://localhost:8000',
      '/backtest': 'http://localhost:8000',
      // añade aquí más rutas si tu backend expone otras
    }
  }
})
