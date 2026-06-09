const isCloudflareExport = process.env.AHE_DEPLOY_TARGET === 'cloudflare';
const basePath = (process.env.AHE_PUBLIC_BASE_PATH ?? '/agent-harness').replace(/\/+$/, '');

/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ['@ahe/harness'],
  ...(isCloudflareExport
    ? { output: 'export', basePath, trailingSlash: true, images: { unoptimized: true } }
    : {})
};

export default nextConfig;
