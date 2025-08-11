import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/',
  server: {
    open: true,
    host: true,
  },
  build: {
    outDir: path.resolve(__dirname, 'static/frontend'),
    manifest: true,        // ✅ tells Vite to generate manifest.json
    rollupOptions: {
      input: path.resolve(__dirname, '/src/main.jsx'),
    },
  },
})
