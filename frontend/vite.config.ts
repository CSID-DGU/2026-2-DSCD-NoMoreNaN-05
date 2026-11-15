import { fileURLToPath, URL } from 'node:url'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig, loadEnv } from 'vite'

const root = fileURLToPath(new URL('.', import.meta.url))

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // VITE_ 접두사가 없는 변수는 브라우저 코드에 노출되지 않아요(서버 주소 보호).
  const env = loadEnv(mode, root, '')
  const apiTarget = env.API_PROXY_TARGET || 'http://localhost:5000'

  return {
    plugins: [react(), tailwindcss()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    server: {
      // 공용 서버에서 띄울 때 바깥(9304 → 5173)에서 접속할 수 있도록
      host: true,
      port: 5173,
      // 5173이 사용 중이면 다른 포트로 옮기지 않고 실패 (포트 연결이 어긋나지 않게)
      strictPort: true,
      proxy: {
        // /api/... 요청을 백엔드로 그대로 전달 (경로의 /api는 유지)
        '/api': {
          target: apiTarget,
          changeOrigin: true,
        },
      },
    },
  }
})
