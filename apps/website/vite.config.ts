import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

// The only build here is the SSR bundle for the prerender step: there is no
// client entry, because the site ships no client JavaScript.
export default defineConfig({
  plugins: [react()],
  build: {
    ssr: true,
    target: 'node20',
    rollupOptions: { output: { format: 'es' } },
    emptyOutDir: true,
  },
});
