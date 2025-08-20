import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

const isProduction = process.env.NODE_ENV === 'production'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [react()],
    base: mode === 'staging'
      ? '/static/frontend/'
      : '/',
    server: {
      open: true,
      host: true,
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        }
      }
    },
    build: {
      outDir: mode === 'staging'
        ? path.resolve(__dirname, '../static/frontend')
        : path.resolve(__dirname, './dist'),
      assetsDir: 'assets',
      emptyOutDir: true,
      manifest: true,
      rollupOptions: {
        input: 'src/main.jsx',
      },
    },
  }
})
