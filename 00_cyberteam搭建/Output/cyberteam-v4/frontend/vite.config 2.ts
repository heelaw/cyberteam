import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        // 后端默认端口 49187，通过环境变量 CLAWTEAM_PORT 覆盖
        target: 'http://localhost:49187',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:49187',
        ws: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
})
