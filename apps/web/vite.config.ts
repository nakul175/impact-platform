import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: { "/v1": "http://127.0.0.1:8000", "/auth": "http://127.0.0.1:8000" },
  },
  build: {
    sourcemap: false,
    rollupOptions: {
      input: { app: "index.html", walkthrough: "ai-walkthrough.html" },
    },
  },
});
