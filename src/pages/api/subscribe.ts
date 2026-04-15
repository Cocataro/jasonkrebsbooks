export const prerender = false;

// MailerLite subscribe endpoint. Deployable on Vercel (Node or Edge function).
// Requires env vars: MAILERLITE_API_TOKEN, MAILERLITE_GROUP_ID (optional).

export async function POST({ request }: { request: Request }) {
  const token = import.meta.env.MAILERLITE_API_TOKEN;
  const groupId = import.meta.env.MAILERLITE_GROUP_ID;

  if (!token) {
    return new Response(JSON.stringify({ error: 'Newsletter not configured.' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  let email = '';
  try {
    const body = await request.json();
    email = (body.email || '').toString().trim();
  } catch {
    return new Response(JSON.stringify({ error: 'Invalid request.' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  if (!email || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
    return new Response(JSON.stringify({ error: 'Please enter a valid email address.' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const payload: Record<string, unknown> = { email };
  if (groupId) {
    payload.groups = [groupId];
  }

  const res = await fetch('https://connect.mailerlite.com/api/subscribers', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (res.ok) {
    return new Response(JSON.stringify({ ok: true }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const errText = await res.text().catch(() => '');
  console.error('MailerLite error', res.status, errText);
  return new Response(JSON.stringify({ error: 'Subscription failed. Try again later.' }), {
    status: 502,
    headers: { 'Content-Type': 'application/json' },
  });
}
