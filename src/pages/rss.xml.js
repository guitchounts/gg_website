import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import site from '../data/site.json';

export async function GET(context) {
  const posts = (await getCollection('blog')).sort((a, b) => b.data.date - a.data.date);
  return rss({
    title: `${site.name} — Blog`,
    description: 'Archive of blog posts on neuroscience, science policy, and philosophy of mind.',
    site: context.site,
    items: posts.map((p) => ({ title: p.data.title, pubDate: p.data.date, description: p.data.excerpt, link: `/blog/${p.id}/` })),
  });
}
