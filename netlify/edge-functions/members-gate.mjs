// Gate for the private partner area. Every request under /members/ needs a valid
// partner session; project pages also need access to that project. Anyone else is
// sent to /login/.
import { getStore } from "@netlify/blobs";
import { userFromRequest, canSee } from "../lib/auth.mjs";

const NOINDEX = "noindex, nofollow, noarchive";

export default async (request, context) => {
  const url = new URL(request.url);
  const store = getStore({ name: "members", consistency: "strong" });
  const user = await userFromRequest(request, store);
  const toLogin = () => Response.redirect(new URL("/login/?next=" + encodeURIComponent(url.pathname), url), 302);
  if (!user) return toLogin();
  const slug = url.pathname.match(/^\/members\/projects\/([a-z0-9-]+)/)?.[1];
  if (slug && !canSee(user, slug)) {
    return new Response(`<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>No access</title>
<body style="font-family:Arial,sans-serif;background:#F6F3EB;color:#13251D;padding:60px 20px;text-align:center">
<h1 style="font-size:1.5rem">You do not have access to this project</h1>
<p>Your account does not include this project. Please contact <a href="mailto:john@guilgal.org">john@guilgal.org</a> to request access.</p>
<p><a href="/members/">Back to the partner portal</a></p></body>`,
      { status: 403, headers: { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store", "X-Robots-Tag": NOINDEX } });
  }
  const res = await context.next();
  res.headers.set("Cache-Control", "private, no-store");
  res.headers.set("X-Robots-Tag", NOINDEX);
  return res;
};

export const config = { path: ["/members", "/members/*"] };
