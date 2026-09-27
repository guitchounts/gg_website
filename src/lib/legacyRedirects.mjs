import fs from 'node:fs';
import path from 'node:path';

/** Build an Astro `redirects` map from legacyUrl frontmatter in content/blog. */
export function legacyRedirects() {
  const dir = path.resolve('content/blog');
  const out = {};
  for (const f of fs.readdirSync(dir)) {
    if (!f.endsWith('.md')) continue;
    const src = fs.readFileSync(path.join(dir, f), 'utf8');
    const m = src.match(/^legacyUrl:\s*"([^"]+)"/m);
    if (m) out[m[1]] = `/blog/${f.replace(/\.md$/, '')}`;
  }
  out['/articles'] = '/writing';
  out['/coming-soon'] = '/';
  return out;
}
