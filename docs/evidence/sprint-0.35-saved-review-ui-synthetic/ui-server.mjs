import { createServer } from "/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform/apps/web/node_modules/vite/dist/node/index.js";
const server = await createServer({
  root: "/private/tmp/tola-ai-plan-review-draft",
  configFile: false,
  server: {
    host: "127.0.0.1",
    port: 8193,
    strictPort: true,
    fs: {
      allow: [
        "/private/tmp/tola-ai-plan-review-draft",
        "/Users/athena/.codex/.chatgpt-projects/g-p-6ab89116b65c81919bb561fed2d716c0/work/impact-platform",
      ],
    },
  },
  esbuild: { jsx: "automatic" },
});
await server.listen();
console.log("Private saved-plan review fixture ready8193");
