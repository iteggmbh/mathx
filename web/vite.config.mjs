// vite.config.js
import { resolve } from 'path'
import { defineConfig } from 'vite'

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        ecc: resolve(__dirname, 'ecc.html'),
        gui: resolve(__dirname, 'gui.html'),
        second: resolve(__dirname, 'second.html'),
      },
    },
  },
  server: {
    proxy: {
      '/mathx': 'http://localhost:8011',
    },
  },
})