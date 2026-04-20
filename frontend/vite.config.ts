import path from 'node:path'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    hmr: {
      host: '127.0.0.1',
      protocol: 'ws',
    },
    proxy: {
      '/auth': {
        target: 'http://backend:8002',
        changeOrigin: true,
      },
      '/products': {
        target: 'http://backend:8002',
        changeOrigin: true,
      },
      '/cart': {
        target: 'http://backend:8002',
        changeOrigin: true,
      },
      '/orders': {
        target: 'http://backend:8002',
        changeOrigin: true,
      },
      '/chats': {
        target: 'http://backend:8002',
        changeOrigin: true,
      },
      '/enterprises': {
        target: 'http://backend:8002',
        changeOrigin: true,
      },
      '/favorites': {
        target: 'http://backend:8002',
        changeOrigin: true,
      },
      '/users': {
        target: 'http://backend:8002',
        changeOrigin: true,
      },
      '/docs': {
        target: 'http://backend:8002',
        changeOrigin: true,
      },
      '/openapi.json': {
        target: 'http://backend:8002',
        changeOrigin: true,
      },
    },
  },
})
