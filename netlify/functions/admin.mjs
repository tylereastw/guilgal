// Admin API for the partner logon (used by /admin/).
//   POST   /api/admin/login   { password, code }   password + authenticator code -> admin cookie (2 hours)
//   POST   /api/admin/logout
//   GET    /api/admin/users                        list partner accounts
//   POST   /api/admin/users   { email, name, projects, password?, disabled? }  create or update
//                                                  (omit password to keep it; set resetPassword: true to generate one)
//   DELETE /api/admin/users?email=...
//   GET    /api/admin/briefs                       which projects have a brief uploaded
//   POST   /api/admin/briefs  multipart: slug, file (PDF, max 15 MB)
//   DELETE /api/admin/briefs?slug=...
import { getStore } from "@netlify/blobs";
import { env, json, sign, cookie, isAdmin, checkTotp, safeEqual, hashPassword, randomPassword, normEmail, publicUser,
         throttled, recordFailure, clearFailures, ADMIN_COOKIE, ADMIN_HOURS, PROJECTS } from "../lib/auth.mjs";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default async (request, context) => {
  const url = new URL(request.url);
  const path = url.pathname.replace(/\/$/, "");
  const members = getStore({ name: "members", consistency: "strong" });

  // JSON writes must come from this site's own pages
  if (request.method !== "GET" && !path.endsWith("/briefs")) {
    const ct = request.headers.get("content-type") || "";
    if (!ct.includes("application/json")) return json({ error: "Expected JSON" }, 415);
  }

  if (path === "/api/admin/login" && request.method === "POST") {
    const pw = env("ADMIN_PASSWORD"), secret = env("ADMIN_TOTP_SECRET");
    if (!pw || !secret || !env("SESSION_SECRET")) return json({ error: "Admin access is not configured. Set ADMIN_PASSWORD, ADMIN_TOTP_SECRET and SESSION_SECRET in Netlify." }, 503);
    const key = "admin:" + (context.ip || "unknown");
    if (await throttled(members, key)) return json({ error: "Too many attempts. Please wait 15 minutes." }, 429);
    let b; try { b = await request.json(); } catch { return json({ error: "Invalid request" }, 400); }
    const ok = safeEqual(String(b.password || ""), pw) && (await checkTotp(secret, String(b.code || "").trim()));
    if (!ok) { await recordFailure(members, key); return json({ error: "Password or authenticator code is incorrect." }, 401); }
    await clearFailures(members, key);
    const token = await sign({ a: 1, x: Date.now() + ADMIN_HOURS * 36e5 });
    return json({ ok: true }, 200, { "Set-Cookie": cookie(ADMIN_COOKIE, token, { maxAge: ADMIN_HOURS * 3600, sameSite: "Strict" }) });
  }
  if (path === "/api/admin/logout") return json({ ok: true }, 200, { "Set-Cookie": cookie(ADMIN_COOKIE, "", { maxAge: 0, sameSite: "Strict" }) });

  if (!(await isAdmin(request))) return json({ error: "Not signed in" }, 401);

  if (path === "/api/admin/users") {
    if (request.method === "GET") {
      const { blobs } = await members.list({ prefix: "users/" });
      const users = [];
      for (const b of blobs) { const u = await members.get(b.key, { type: "json" }); if (u) users.push(publicUser(u)); }
      users.sort((a, b) => a.email.localeCompare(b.email));
      return json({ users, projects: PROJECTS });
    }
    if (request.method === "POST") {
      let b; try { b = await request.json(); } catch { return json({ error: "Invalid request" }, 400); }
      const email = normEmail(b.email);
      if (!EMAIL_RE.test(email)) return json({ error: "Enter a valid email address." }, 400);
      const projects = (Array.isArray(b.projects) ? b.projects : []).filter((p) => p === "*" || PROJECTS[p]);
      const existing = await members.get("users/" + email, { type: "json" });
      const user = existing || { email, created: new Date().toISOString(), ver: 0 };
      user.name = String(b.name ?? user.name ?? "").slice(0, 120);
      user.projects = projects;
      if (typeof b.disabled === "boolean") { if (b.disabled && !user.disabled) user.ver = (user.ver || 0) + 1; user.disabled = b.disabled; }
      let issued = null;
      let password = b.password ? String(b.password) : null;
      if (!password && (b.resetPassword || !existing)) password = issued = randomPassword();
      if (password) {
        if (password.length < 10) return json({ error: "Passwords must be at least 10 characters." }, 400);
        Object.assign(user, await hashPassword(password));
        if (existing) user.ver = (user.ver || 0) + 1; // signs out existing sessions
      }
      await members.setJSON("users/" + email, user);
      return json({ ok: true, user: publicUser(user), password: issued });
    }
    if (request.method === "DELETE") {
      const email = normEmail(url.searchParams.get("email"));
      await members.delete("users/" + email);
      return json({ ok: true });
    }
  }

  if (path === "/api/admin/briefs") {
    const briefs = getStore({ name: "briefs", consistency: "strong" });
    if (request.method === "GET") {
      const out = {};
      for (const slug of Object.keys(PROJECTS)) {
        const m = await briefs.getMetadata(slug);
        out[slug] = m ? { filename: m.metadata?.filename || slug + ".pdf", uploaded: m.metadata?.uploaded || null, size: m.metadata?.size || null } : null;
      }
      return json({ briefs: out, projects: PROJECTS });
    }
    if (request.method === "POST") {
      const form = await request.formData();
      const slug = String(form.get("slug") || "");
      const file = form.get("file");
      if (!PROJECTS[slug]) return json({ error: "Unknown project" }, 400);
      if (!file || typeof file === "string") return json({ error: "Choose a PDF file." }, 400);
      if (file.size > 15 * 1024 * 1024) return json({ error: "The file must be 15 MB or smaller." }, 400);
      const data = await file.arrayBuffer();
      if (new TextDecoder().decode(new Uint8Array(data).slice(0, 5)) !== "%PDF-") return json({ error: "The file must be a PDF." }, 400);
      await briefs.set(slug, data, { metadata: { filename: file.name || slug + ".pdf", type: "application/pdf", size: file.size, uploaded: new Date().toISOString() } });
      return json({ ok: true });
    }
    if (request.method === "DELETE") {
      const slug = url.searchParams.get("slug");
      if (!PROJECTS[slug]) return json({ error: "Unknown project" }, 400);
      await briefs.delete(slug);
      return json({ ok: true });
    }
  }

  return json({ error: "Not found" }, 404);
};

export const config = { path: ["/api/admin/*"] };
