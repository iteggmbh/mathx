// vite.config.js
import { resolve } from 'path'
import { defineConfig } from 'vite'

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        ecc: resolve(__dirname, 'ecc.html')
      },
    },
  },
})