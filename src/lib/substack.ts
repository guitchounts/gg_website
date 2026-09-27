/**
 * Fetch the Of Two Minds Substack feed at build time.
 * Falls back to a checked-in snapshot if the network is unavailable, so the
 * build never fails because of Substack. A scheduled GitHub Action rebuilds
 * the site daily so the homepage stays current without manual work.
 */
import { XMLParser } from 'fast-xml-parser';
import fs from 'node:fs';
import path from 'node:path';

export const OTM_URL = 'https://oftwominds.substack.com';
const FEED_URL = `${OTM_URL}/feed`;
const FALLBACK = path.resolve('src/data/otm_feed_fallback.xml');

export interface OtmPost {
  title: string;
  link: string;
  date: Date;
  author: string;
  description: string;
  image?: string;
}

function parse(xml: string): OtmPost[] {
  const parser = new XMLParser({ ignoreAttributes: false, attributeNamePrefix: '@_' });
  const doc = parser.parse(xml);
  const items = doc?.rss?.channel?.item ?? [];
  return (Array.isArray(items) ? items : [items])
    .map((it: any) => ({
      title: String(it.title ?? '').trim(),
      link: String(it.link ?? '').trim(),
      date: new Date(it.pubDate),
      author: String(it['dc:creator'] ?? '').trim(),
      description: String(it.description ?? '').replace(/<[^>]+>/g, '').trim(),
      image: it.enclosure?.['@_url'] as string | undefined,
    }))
    .filter((p) => p.title && p.title.toLowerCase() !== 'coming soon')
    .sort((a, b) => b.date.getTime() - a.date.getTime());
}

let cache: OtmPost[] | null = null;

export async function getOtmPosts(): Promise<OtmPost[]> {
  if (cache) return cache;
  try {
    const res = await fetch(FEED_URL, { signal: AbortSignal.timeout(10_000) });
    if (!res.ok) throw new Error(`feed ${res.status}`);
    const xml = await res.text();
    cache = parse(xml);
    fs.writeFileSync(FALLBACK, xml); // refresh the snapshot
  } catch (err) {
    console.warn('[substack] live feed unavailable, using snapshot:', (err as Error).message);
    cache = parse(fs.readFileSync(FALLBACK, 'utf8'));
  }
  return cache;
}
