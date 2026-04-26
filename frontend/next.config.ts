import type { NextConfig } from "next";

const isProd = process.env.NODE_ENV === 'production';

const nextConfig: NextConfig = {
  output: 'export',
  images: {
    unoptimized: true,
  },
  // Only use basePath/assetPrefix in production (GitHub Pages)
  basePath: isProd ? '/land-risk-api' : '',
  assetPrefix: isProd ? '/land-risk-api' : '',
};

export default nextConfig;
