import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

// Two builds. `vite build` produces the client bundle that hydrates the page
// (the animated pieces need it); `vite build --ssr src/entry-static.tsx`
// produces the prerenderer, which then writes the HTML. The manifest is what
// lets the prerenderer name the hashed asset files in the <head>.
export default defineConfig({
  plugins: [react()],
  build: {
    manifest: true,
    target: 'es2022',
    rollupOptions: { input: 'src/entry-client.tsx' },
  },
});
