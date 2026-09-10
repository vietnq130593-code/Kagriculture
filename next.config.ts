import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  typescript: {
    ignoreBuildErrors: true,
  },
  reactStrictMode: false,
  // 4GB-RAM sandbox: the arena page (recharts + socket.io + 50×50 grid) made
  // webpack dev balloon to ~2.9GB RSS → kernel OOM-killed next-server mid-battle
  // (preview panel disconnect). Slash webpack dev memory.
  experimental: {
    webpackMemoryOptimizations: true,
  },
};

export default nextConfig;
