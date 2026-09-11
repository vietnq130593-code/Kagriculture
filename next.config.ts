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
  // 2026-09-11: cold webpack compile (cache wiped in the OOM cascade) needs
  // ~3.5GB RSS and the box only frees ~3.46GB — OOM-killed 5× in a loop.
  // The dominant memory hog is dev source-map chains. The CLI flag
  // `--disable-source-maps` is not honored by `next dev` (webpack config
  // wins), so force it here. This cut the cold compile under the ceiling.
  webpack: (config, { dev }) => {
    if (dev) {
      config.devtool = false;
    }
    return config;
  },
};

export default nextConfig;
