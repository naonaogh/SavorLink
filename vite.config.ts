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
    host: '127.0.0.1',          // ← строго IPv4-адрес вместо 'localhost'
    port: 5173,
    strictPort: true,           // если порт занят — сразу ошибка
    hmr: {
      host: '127.0.0.1',        // для hot-reload тоже IPv4
      protocol: 'ws',           // иногда помогает с VPN
    },
  },
})



