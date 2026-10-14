import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // TODO (toi) : quand le back-end FastAPI tournera, tu pourras proxyfier
    // les appels API pour éviter les soucis de CORS en développement :
    //
    // proxy: {
    //   "/api": {
    //     target: "http://localhost:8000",
    //     changeOrigin: true,
    //   },
    // },
  },
});
