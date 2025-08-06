import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/',
  server: {
    open: true,
    host: true,
  },
  build: {
    outDir: 'dist',        // default, optional
    manifest: true,        // ✅ tells Vite to generate manifest.json
    rollupOptions: {
      input: '/src/main.jsx', // change this if your entry is elsewhere
    },
  },
})
