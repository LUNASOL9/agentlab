import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // 개발 서버(npm run dev) 설정이에요.
  server: {
    // proxy: /api로 시작하는 요청은 백엔드(FastAPI)로 넘겨요.
    // 브라우저는 화면(5173)에만 요청하니까, 다른 주소로 요청할 때 생기는 문제(CORS)가 없어요.
    // 127.0.0.1: localhost라고 쓰면 Windows에서 접속이 한참 멈출 수 있어요. (2단계와 같아요)
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
})
