import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { copyFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const forgeRoot = dirname(fileURLToPath(import.meta.url))

const publishInstallers = {
  name: 'publish-installers',
  closeBundle() {
    copyFileSync(resolve(forgeRoot, '../install.sh'), resolve(forgeRoot, 'dist/install.sh'))
    copyFileSync(resolve(forgeRoot, '../install.ps1'), resolve(forgeRoot, 'dist/install.ps1'))
  },
}

export default defineConfig({
  plugins: [react(), tailwindcss(), publishInstallers],
  server: {
    host: '0.0.0.0',
    port: 4173,
    strictPort: true,
  },
  preview: {
    host: '0.0.0.0',
    port: 4173,
  },
})
