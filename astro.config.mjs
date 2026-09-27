// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { legacyRedirects } from './src/lib/legacyRedirects.mjs';

export default defineConfig({
  site: 'https://www.guitchounts.com',
  trailingSlash: 'ignore',
  integrations: [sitemap()],
  // Old Squarespace blog URLs (/blog/2017/1/2/slug) -> new /blog/slug pages,
  // generated from the `legacyUrl` field in each post's frontmatter.
  redirects: legacyRedirects(),
  markdown: { shikiConfig: { theme: 'github-light' } },
});
