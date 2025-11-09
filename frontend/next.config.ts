import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  /* config options here */
  // Note: For Apple Pay to work, the site must be served over HTTPS
  // HTTPS is configured via custom server (server.js) or Docker reverse proxy
  // For production, ensure your deployment uses HTTPS

  // Disable Turbopack to avoid internal errors
  // Use webpack instead (more stable for development)
  // Turbopack can be unstable in Docker environments
  // Disabled via NEXT_TURBO=0 environment variable in docker-compose.yml

  // Allow cross-origin requests for development (fixes webpack-hmr warning)
  allowedDevOrigins: [
    'https://localhost:3443',
    'https://127.0.0.1:3443',
    'https://localhost:3443',
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:3000',
  ],

  // Configure webpack for custom server with polling-based HMR
  webpack: (config, { dev, isServer }) => {
    if (dev && !isServer) {
      // Use polling for file watching (better for Docker/containers)
      config.watchOptions = {
        poll: 1000,
        aggregateTimeout: 300,
      };
    }
    
    // Ensure path aliases work correctly for both server and client
    if (config.resolve) {
      config.resolve.alias = {
        ...config.resolve.alias,
        '@': path.resolve(__dirname),
      };
    }
    
    return config;
  },
};

export default nextConfig;
