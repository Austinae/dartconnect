import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Project site: https://<user>.github.io/dartconnect/
const base = process.env.GITHUB_PAGES === "true" ? "/dartconnect/" : "/";

export default defineConfig({
  base,
  plugins: [react()],
});