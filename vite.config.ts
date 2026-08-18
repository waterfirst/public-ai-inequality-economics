import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  base: "/public-ai-inequality-economics/",
  server: { host: "0.0.0.0", allowedHosts: ["terminal.local"] },
  build: {
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes("/node_modules/three/")) return "three";
          if (id.includes("/node_modules/react") || id.includes("/node_modules/lucide-react")) return "react";
          return undefined;
        },
      },
    },
  },
});
