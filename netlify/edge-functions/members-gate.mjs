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

// Public pages that list projects. Each project card is in the page twice (named and
// confidential) and each project is an option in the enquiry form; this keeps only what the
// admin panel allows: named, confidential (no name or details) or hidden. Default: confidential.
const LISTING_PAGES = new Set(["/", "/index.html", "/projects", "/projects/", "/projects/index.html",
  "/contact/", "/contact/index.html", "/investors/", "/investors/index.html"]);
export async function listingModes(store) {
  try { return (await store.get("config/public-projects", { type: "json" })) || {}; } catch { return {}; }
}
export function applyListing(html, modes) {
  const mode = sl => (["named", "confidential", "hidden"].includes(modes[sl]) ? modes[sl] : "confidential");
  let shown = 0;
  let out = html.replace(/<li class="psum[^"]*" data-pslug="([a-z0-9-]+)" data-pvariant="(named|opaque)">[\s\S]*?<\/li>/g, (m, sl, v) => {
    const keep = (v === "named" && mode(sl) === "named") || (v === "opaque" && mode(sl) === "confidential");
    if (keep) shown++;
    return keep ? m : "";
  });
  out = out.replace(/<option data-pslug="([a-z0-9-]+)">[^<]*<\/option>/g, (m, sl) => (mode(sl) === "named" ? m.replace(/ data-pslug="[a-z0-9-]+"/, "") : ""));
  if (!shown) out = out.replace("data-psums-none hidden", "data-psums-none");
  return out;
}
async function publicListing(context, store) {
  const res = await context.next();
  if (!(res.headers.get("content-type") || "").includes("text/html")) return res;
  const out = applyListing(await res.text(), await listingModes(store));
  const headers = new Headers(res.headers);
  headers.delete("content-length");
  headers.set("Cache-Control", "public, max-age=0, must-revalidate");
  return new Response(out, { status: res.status, headers });
}

// Tracked links: a visit to an investor page carrying ?utm_source=... (for example from
// LinkedIn) adds one to a daily counter for that page and source. Only counts, no personal
// data or cookies, so it works whether or not the visitor accepts analytics. Link-preview
// robots (LinkedIn, Slack, WhatsApp and similar) and repeat loads are not counted.
// Short tracking codes: a link ending in ?li counts as LinkedIn, ?em as email and so on.
// Full ?utm_source=... links are still counted.
export const SHORT_SOURCES = { li: "linkedin", em: "email", wa: "whatsapp", x: "twitter", fb: "facebook", ig: "instagram", qr: "qr", o: "other" };
export function trackedSource(url) {
  const utm = url.searchParams.get("utm_source");
  if (utm) return utm;
  for (const k of url.searchParams.keys()) if (SHORT_SOURCES[k.toLowerCase()]) return SHORT_SOURCES[k.toLowerCase()];
  return null;
}
const BOT_RE = /bot|crawl|spider|preview|linkedin|facebookexternalhit|slack|whatsapp|telegram|discord|skype|embedly|quora|pinterest|vkshare|w3c_validator|headless|lighthouse|curl|wget|python|node-fetch/i;
export function clickKey(path, source, day) {
  const page = path.replace(/^\/opportunities\//, "").replace(/\/?(index\.html)?$/, "").replace(/[^a-z0-9-]/g, "") || "page";
  const src = String(source).toLowerCase().replace(/[^a-z0-9_-]/g, "").slice(0, 40) || "other";
  return `clicks/${page}/${src}/${day}`;
}
async function countVisit(request, url, path, context) {
  try {
    if (request.method !== "GET" || BOT_RE.test(request.headers.get("user-agent") || "")) return;
    if (request.headers.get("purpose") === "prefetch" || request.headers.get("sec-purpose")) return;
    const store = getStore({ name: "members", consistency: "strong" });
    const key = clickKey(path, trackedSource(url), new Date().toISOString().slice(0, 10));
    const n = Number((await store.get(key)) || 0);
    await store.set(key, String(n + 1));
  } catch { /* never block the page over a counter */ }
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
  if (!members && !archive) {
    // Public pages: tidy doubled slashes (//contact/) so relative links stay clean.
    if (request.method === "GET" && /\/\/|\\/.test(url.pathname)) return Response.redirect(new URL(norm + url.search, url), 301);
    if (LISTING_PAGES.has(low)) return publicListing(context, getStore({ name: "members", consistency: "strong" }));
    if (low.startsWith("/opportunities/") && trackedSource(url)) await countVisit(request, url, low, context);
    return; // carry on as normal
  }

  // Send odd spellings to the one canonical address, which is then checked below.
  // Partner files are all lower case; archive files keep their case (the check above is case-blind).
  const canonical = members ? low : norm;
  if (decodeURIComponent(url.pathname) !== canonical) return Response.redirect(new URL(canonical + url.search, url), 301);

  const store = getStore({ name: "members", consistency: "strong" });
  if (archive) {
    if (!(await isAdmin(request, store))) return Response.redirect(new URL("/admin/", url), 302);
    return privateHeaders(await context.next());
  }
  // Admins can open everything under /members/, even when the same browser is also
  // signed in as a partner (checked first, so a partner session never limits an admin).
  if (await isAdmin(request, store)) return privateHeaders(await context.next());
  const user = await userFromRequest(request, store);
  if (!user) return Response.redirect(new URL("/login/?next=" + encodeURIComponent(canonical), url), 302);
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
