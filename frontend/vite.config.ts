import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: true,
    port: 5173,
    watch: {
      usePolling: true
    },
    allowedHosts: [
      "http://localhost:8000",
      "http://127.0.0.1:8000",
      "http://localhost:8001",
      "http://127.0.0.1:8001",
    ]
  }
})
