// Gate for private content. Runs on every request so that URL variants cannot slip
// past it: the static file server treats //members, /%2Fmembers and /MEMBERS as the
// same file as /members, so the check is made on a normalised copy of the path.
// - /members/: needs a valid partner session; project pages and project images also need
//   access to that project. The portal page is filtered here, on the server, so a partner's
//   browser never receives the names of projects they are not assigned. Admins can open
//   everything under /members/. Anyone else is sent to /login/.
// - /archive/: the saved previous design, which contains copies of the project pages.
//   Admins only; anyone else is sent to /admin/.
import { getStore } from "@netlify/blobs";
import { userFromRequest, canSee, isAdmin } from "../lib/auth.mjs";

const NOINDEX = "noindex, nofollow, noarchive";
// Longest first, so "ndela-mpaza" is matched before any shorter slug it starts with.
const MEDIA_SLUGS = ["nizi-baluma", "ndela-mpaza", "hydropower", "pumba", "alpha", "tumfa"];

// Decode, turn backslashes into slashes and collapse repeated slashes.
export function normalisePath(pathname) {
  let p;
  try { p = decodeURIComponent(pathname); } catch { return null; }
  return p.replace(/\\/g, "/").replace(/\/{2,}/g, "/");
}

const privateHeaders = res => {
  res.headers.set("Cache-Control", "private, no-store");
  res.headers.set("X-Robots-Tag", NOINDEX);
  return res;
};

export default async (request, context) => {
  const url = new URL(request.url);
  const norm = normalisePath(url.pathname);
  if (norm === null) return new Response("Bad request", { status: 400 });
  const low = norm.toLowerCase();
  const members = /^\/members(\/|$)/.test(low);
  const archive = /^\/archive(\/|$)/.test(low);
  if (!members && !archive) return; // public page: carry on as normal

  // Send odd spellings to the one canonical address, which is then checked below.
  // Partner files are all lower case; archive files keep their case (the check above is case-blind).
  const canonical = members ? low : norm;
  if (decodeURIComponent(url.pathname) !== canonical) return Response.redirect(new URL(canonical + url.search, url), 301);

  const store = getStore({ name: "members", consistency: "strong" });
  if (archive) {
    if (!(await isAdmin(request, store))) return Response.redirect(new URL("/admin/", url), 302);
    return privateHeaders(await context.next());
  }
  const user = await userFromRequest(request, store);
  if (!user) {
    if (await isAdmin(request, store)) return privateHeaders(await context.next());
    return Response.redirect(new URL("/login/?next=" + encodeURIComponent(canonical), url), 302);
  }
  // Project-only files: the manifest is for admins; images are named after their project.
  if (low.startsWith("/members/media/")) {
    const file = low.slice("/members/media/".length);
    const owner = MEDIA_SLUGS.find(sl => file.startsWith(sl + "-") || file === "card-" + sl + ".jpg" || file.startsWith("card-" + sl + "."));
    if (file === "projects.json" || !owner || !canSee(user, owner)) return new Response("Not found", { status: 404, headers: { "Cache-Control": "no-store" } });
    return privateHeaders(await context.next());
  }
  const slug = low.match(/^\/members\/projects\/([a-z0-9-]+)/)?.[1];
  if (low === "/members/" || low === "/members" || low === "/members/index.html") {
    const res = await context.next();
    const html = await res.text();
    let shown = 0;
    let out = html.replace(/<li class="pcard" data-slug="([a-z0-9-]+)">[\s\S]*?<\/li>/g, (m, sl) => (canSee(user, sl) ? (shown++, m) : ""));
    if (!shown) out = out.replace("data-none hidden", "data-none");
    const headers = new Headers(res.headers);
    headers.delete("content-length");
    return privateHeaders(new Response(out, { status: res.status, headers }));
  }
  if (slug && !canSee(user, slug)) {
    return new Response(`<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>No access</title>
<body style="font-family:Arial,sans-serif;background:#F6F3EB;color:#13251D;padding:60px 20px;text-align:center">
<h1 style="font-size:1.5rem">You do not have access to this project</h1>
<p>Your account does not include this project. Please contact <a href="mailto:john@guilgal.org">john@guilgal.org</a> to request access.</p>
<p><a href="/members/">Back to the partner portal</a></p></body>`,
      { status: 403, headers: { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store", "X-Robots-Tag": NOINDEX } });
  }
  return privateHeaders(await context.next());
};

export const config = { path: "/*" };
