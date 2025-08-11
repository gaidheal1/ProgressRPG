import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/static/frontend/',
  server: {
    open: true,
    host: true,
  },
  build: {
    outDir: path.resolve(__dirname, '../static/'),
    assetsDir: 'frontend/assets',
    emptyOutDir: true,
    manifest: true,
    rollupOptions: {
      input: 'src/main.jsx',
    },
  },
})
