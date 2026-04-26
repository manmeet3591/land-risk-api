import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'export',
  images: {
    unoptimized: true,
  },
  // This matches your repository name for GitHub Pages
  basePath: '/land-risk-api',
  assetPrefix: '/land-risk-api',
};

export default nextConfig;
