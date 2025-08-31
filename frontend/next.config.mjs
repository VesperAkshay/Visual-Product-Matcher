/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001/api',
  },
  images: {
    domains: ['localhost', 'your-backend-app.onrender.com'],
    unoptimized: true, // For better compatibility with external image sources
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001/api'}/:path*`,
      },
    ];
  },
};

export default nextConfig;
