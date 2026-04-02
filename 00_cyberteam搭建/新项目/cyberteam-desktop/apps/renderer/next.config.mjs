import path from 'node:path'

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  outputFileTracingRoot: path.resolve(process.cwd(), '../..'),
  images: {
    unoptimized: true,
  },
  experimental: {
    externalDir: true,
  },
}

export default nextConfig
