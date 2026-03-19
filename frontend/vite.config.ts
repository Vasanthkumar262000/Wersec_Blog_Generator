import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        timeout: 300000, // 5 min — blog generation (research + write + LinkedIn + thumbnail) can take 60–120s
      },
      '/api/outputs': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
