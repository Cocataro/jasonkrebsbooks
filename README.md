# jasonkrebsbooks.com

Author platform for Jason Krebs — cozy fantasy novelist. Static Astro site deployed on Vercel.

## Stack
- **Astro 5** — static site generator
- **MDX** — blog posts in markdown
- **Vercel** — hosting + serverless function for newsletter subscribe
- **MailerLite** — newsletter provider
- **Cloudflare / Hostinger DNS** — domain points to Vercel

## Structure
```
src/
  layouts/       site-wide layout
  components/    reusable UI (Newsletter, etc.)
  content/
    posts/       blog posts as markdown (frontmatter: title, description, publishedAt, tags)
  pages/         routes
    index.astro      landing
    about.astro      pen-persona bio
    books/           book catalog
    blog/            blog listing + post pages
    api/subscribe.ts Vercel serverless function → MailerLite
    news.astro       branded short link → /about#newsletter
    follow.astro     branded short link → Amazon author page
    review.astro     branded short link → Amazon review
    rss.xml.js       RSS feed for Amazon Author Central
public/
  favicon.svg
  robots.txt
```

## Local dev
```bash
npm install
cp .env.example .env.local    # add your MailerLite token
npm run dev                   # localhost:4321
```

## Deploy
Auto-deploys to Vercel on git push to `main`. Env vars set in Vercel dashboard:
- `MAILERLITE_API_TOKEN`
- `MAILERLITE_GROUP_ID` (optional — if you create a specific group)
- `PUBLIC_SITE_URL` (https://jasonkrebsbooks.com)

## Back-matter short links
For Kindle/print back-matter CTAs, use:
- `jasonkrebsbooks.com/news` → newsletter signup
- `jasonkrebsbooks.com/follow` → Amazon author follow
- `jasonkrebsbooks.com/review` → Amazon review prompt

Destinations can be updated in the respective `.astro` files without re-uploading books.

## Ownership
- **Author / Board:** Nicole (pen name: Jason Krebs)
- **Content authoring (Phase 1):** Nina Kowalski (Paperclip agent) — blog + newsletter
- **Content authoring (Phase 2):** Riley Bennett (Marketing Lead, when hired) takes over
