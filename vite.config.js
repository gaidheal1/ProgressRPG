import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    open: true, // Automatically open in browser on start
    proxy: {
        '/': 'http://localhost:8000',
    },
  },
});
