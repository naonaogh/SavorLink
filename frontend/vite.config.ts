import path from 'node:path'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

const API_PROXY_PATHS = [
  '/auth',
  '/products',
  '/cart',
  '/orders',
  '/chats',
  '/enterprises',
  '/favorites',
  '/platform-reviews',
  '/users',
  '/docs',
  '/openapi.json',
]

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const proxyTarget = env.VITE_DEV_PROXY_TARGET || 'http://127.0.0.1:8002'

  // Пути SPA (/auth, /cart, /favorites) совпадают с префиксами API. Когда браузер открывает
  // страницу (Accept: text/html), отдаём приложение, а не JSON бэкенда — иначе F5 ломает страницу.
  // Документацию FastAPI (/docs, /openapi.json) по-прежнему проксируем.
  const BACKEND_PAGES = ['/docs', '/openapi.json']
  const serveSpaForPageLoads = (req: { url?: string; headers: Record<string, string | string[] | undefined> }) => {
    const accept = String(req.headers.accept ?? '')
    const isPageLoad = req.headers['sec-fetch-mode'] === 'navigate' || accept.includes('text/html')
    if (isPageLoad && !BACKEND_PAGES.some((p) => req.url?.startsWith(p))) return '/index.html'
    return undefined
  }

  const proxy = Object.fromEntries(
    API_PROXY_PATHS.map((route) => [
      route,
      {
        target: proxyTarget,
        changeOrigin: true,
        bypass: serveSpaForPageLoads,
      },
    ]),
  )

  return {
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
      proxy,
    },
  }
})
