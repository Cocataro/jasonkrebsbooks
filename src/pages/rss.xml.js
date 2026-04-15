import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';

export async function GET(context) {
  const posts = (await getCollection('posts')).filter((p) => !p.data.draft);

  return rss({
    title: 'Jason Krebs — Cozy Fantasy',
    description: 'Notes from Jason Krebs on cozy fantasy, reading, and writing.',
    site: context.site,
    items: posts.map((post) => ({
      title: post.data.title,
      description: post.data.description,
      pubDate: post.data.publishedAt,
      link: `/blog/${post.slug}/`,
    })),
    customData: `<language>en-us</language>`,
  });
}
