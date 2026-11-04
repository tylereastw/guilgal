// Admin API for the partner logon (used by /admin/).
//   GET    /api/admin/status                       { configured, needsSetup }
//   POST   /api/admin/setup   { password }         first run only: new authenticator key + QR code
//   POST   /api/admin/setup/confirm { password, code }  saves the key once a code from the app matches
//   POST   /api/admin/login   { email?, password, code }  main admin (no email) or a named admin -> admin cookie (2 hours)
//   GET    /api/admin/admins                        list named admins          (signed-in admins only)
//   POST   /api/admin/admins  { email, name }       add an admin or renew their invite link -> { inviteUrl }
//   DELETE /api/admin/admins?email=...              remove a named admin
//   POST   /api/admin/invite/start  { token }       invite link: new authenticator key + QR code
//   POST   /api/admin/invite/finish { token, password, code }  sets password and authenticator, signs in
//   POST   /api/admin/logout
//   GET    /api/admin/users                        list partner accounts
//   POST   /api/admin/users   { email, name, projects, password?, disabled? }  create or update
//                                                  (omit password to keep it; set resetPassword: true to generate one)
//   DELETE /api/admin/users?email=...
import { getStore } from "@netlify/blobs";
import QRCode from "qrcode";
import { env, json, sign, cookie, isAdmin, adminFromRequest, checkPassword, sha256hex, randomToken, checkTotp, safeEqual, hashPassword, randomPassword, normEmail, publicUser,
         throttled, recordFailure, clearFailures, adminTotpSecret, newTotpSecret, totpUri, ADMIN_COOKIE, ADMIN_HOURS, PROJECTS } from "../lib/auth.mjs";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default async (request, context) => {
  const url = new URL(request.url);
  const path = url.pathname.replace(/\/$/, "");
  const members = getStore({ name: "members", consistency: "strong" });

  // JSON writes must come from this site's own pages
  if (request.method === "POST") {
    const ct = request.headers.get("content-type") || "";
    if (!ct.includes("application/json")) return json({ error: "Expected JSON" }, 415);
  }
  // Admin cookie is SameSite=Strict, so other sites cannot send DELETE or upload requests with it.

  const pw = env("ADMIN_PASSWORD");
  const ipKey = "admin:" + (context.ip || "unknown");
  const readBody = async () => { try { return await request.json(); } catch { return null; } };
  const passwordOk = (b) => !!pw && safeEqual(String(b?.password || ""), pw);
  const INVITE_DAYS = 7;
  const publicAdmin = (a) => ({ email: a.email, name: a.name || "", status: a.hash ? (a.disabled ? "paused" : "active") : "invited",
    created: a.created || null, lastLogin: a.lastLogin || null, inviteExpires: a.hash ? null : a.invite?.expires || null });
  const inviteFor = async (token) => {
    if (!token || token.length < 20) return null;
    const email = await members.get("admin-invites/" + (await sha256hex(token)));
    const a = email && (await members.get("admins/" + email, { type: "json" }));
    if (!a || !a.invite || a.invite.expires < Date.now()) return null;
    return a;
  };
  const startSession = async (admin) => {
    const payload = { a: 1, x: Date.now() + ADMIN_HOURS * 36e5 };
    if (admin) { payload.u = admin.email; payload.v = admin.ver || 0; }
    const token = await sign(payload, members);
    return json({ ok: true }, 200, { "Set-Cookie": cookie(ADMIN_COOKIE, token, { maxAge: ADMIN_HOURS * 3600, sameSite: "Strict" }) });
  };

  if (path === "/api/admin/status") {
    const me = await adminFromRequest(request, members);
    return json({ configured: !!pw, needsSetup: !!pw && !(await adminTotpSecret(members)), signedIn: !!me,
      me: me ? { owner: !!me.owner, email: me.email, name: me.name || "" } : null });
  }

  // Invite links: a new admin sets their own password and authenticator.
  if (path.startsWith("/api/admin/invite/") && request.method === "POST") {
    if (await throttled(members, ipKey)) return json({ error: "Too many attempts. Please wait 15 minutes." }, 429);
    const b = await readBody();
    const a = await inviteFor(String(b?.token || ""));
    if (!a) { await recordFailure(members, ipKey); return json({ error: "This invite link is not valid or has expired. Ask an admin for a new one." }, 404); }
    if (path === "/api/admin/invite/start") {
      a.pendingTotp = newTotpSecret();
      await members.setJSON("admins/" + a.email, a);
      const uri = totpUri(a.pendingTotp, a.email);
      const svg = await QRCode.toString(uri, { type: "svg", margin: 2, color: { dark: "#10291F", light: "#FFFFFF" } });
      return json({ email: a.email, name: a.name || "", secret: a.pendingTotp, qr: svg });
    }
    if (path === "/api/admin/invite/finish") {
      const password = String(b.password || "");
      if (password.length < 12) return json({ error: "Choose a password of at least 12 characters." }, 400);
      if (!a.pendingTotp) return json({ error: "Reload the invite link and scan the code again." }, 400);
      if (!(await checkTotp(a.pendingTotp, String(b.code || "").trim()))) { await recordFailure(members, ipKey); return json({ error: "That code does not match. Check the time on your phone and try the newest code." }, 401); }
      Object.assign(a, await hashPassword(password));
      a.totp = a.pendingTotp; delete a.pendingTotp;
      await members.delete("admin-invites/" + a.invite.hash); delete a.invite;
      a.ver = (a.ver || 0) + 1; a.lastLogin = Date.now();
      await members.setJSON("admins/" + a.email, a);
      await clearFailures(members, ipKey);
      return startSession(a);
    }
  }

  if (path.startsWith("/api/admin/setup") && request.method === "POST") {
    if (!pw) return json({ error: "Set ADMIN_PASSWORD in Netlify first." }, 503);
    if (await adminTotpSecret(members)) return json({ error: "The authenticator is already set up." }, 403);
    if (await throttled(members, ipKey)) return json({ error: "Too many attempts. Please wait 15 minutes." }, 429);
    const b = await readBody();
    if (!passwordOk(b)) { await recordFailure(members, ipKey); return json({ error: "Admin password is incorrect." }, 401); }
    if (path === "/api/admin/setup") {
      const secret = newTotpSecret();
      await members.set("config/admin-totp-pending", secret);
      const uri = totpUri(secret);
      const svg = await QRCode.toString(uri, { type: "svg", margin: 2, color: { dark: "#10291F", light: "#FFFFFF" } });
      return json({ secret, uri, qr: svg });
    }
    if (path === "/api/admin/setup/confirm") {
      const pending = await members.get("config/admin-totp-pending");
      if (!pending) return json({ error: "Start the setup again." }, 400);
      if (!(await checkTotp(pending, String(b.code || "").trim()))) { await recordFailure(members, ipKey); return json({ error: "That code does not match. Check the time on your phone and try the newest code." }, 401); }
      await members.set("config/admin-totp", pending);
      await members.delete("config/admin-totp-pending");
      await clearFailures(members, ipKey);
      return startSession();
    }
  }

  if (path === "/api/admin/login" && request.method === "POST") {
    if (await throttled(members, ipKey)) return json({ error: "Too many attempts. Please wait 15 minutes." }, 429);
    const b = await readBody();
    const email = normEmail(b?.email);
    if (email) {
      const emailKey = "admin-email:" + email;
      if (await throttled(members, emailKey)) return json({ error: "Too many attempts. Please wait 15 minutes." }, 429);
      const a = await members.get("admins/" + email, { type: "json" });
      const ok = !!a && !a.disabled && !!a.hash && (await checkPassword(String(b.password || ""), a)) && (await checkTotp(a.totp, String(b.code || "").trim()));
      if (!ok) { await recordFailure(members, ipKey); await recordFailure(members, emailKey); return json({ error: "Email, password or authenticator code is incorrect." }, 401); }
      await clearFailures(members, ipKey); await clearFailures(members, emailKey);
      a.lastLogin = Date.now(); await members.setJSON("admins/" + email, a);
      return startSession(a);
    }
    if (!pw) return json({ error: "Admin access is not configured. Set ADMIN_PASSWORD in Netlify." }, 503);
    const secret = await adminTotpSecret(members);
    if (!secret) return json({ error: "Set up the authenticator first.", needsSetup: true }, 409);
    const ok = passwordOk(b) && (await checkTotp(secret, String(b?.code || "").trim()));
    if (!ok) { await recordFailure(members, ipKey); return json({ error: "Password or authenticator code is incorrect." }, 401); }
    await clearFailures(members, ipKey);
    return startSession();
  }
  if (path === "/api/admin/logout") return json({ ok: true }, 200, { "Set-Cookie": cookie(ADMIN_COOKIE, "", { maxAge: 0, sameSite: "Strict" }) });

  const me = await adminFromRequest(request, members);
  if (!me) return json({ error: "Not signed in" }, 401);

  if (path === "/api/admin/admins") {
    if (request.method === "GET") {
      const { blobs } = await members.list({ prefix: "admins/" });
      const admins = [];
      for (const x of blobs) { const a = await members.get(x.key, { type: "json" }); if (a) admins.push(publicAdmin(a)); }
      admins.sort((x, y) => x.email.localeCompare(y.email));
      return json({ admins, me: { owner: !!me.owner, email: me.email } });
    }
    if (request.method === "POST") {
      const b = await readBody();
      const email = normEmail(b?.email);
      if (!EMAIL_RE.test(email)) return json({ error: "Enter a valid email address." }, 400);
      const a = (await members.get("admins/" + email, { type: "json" })) || { email, created: new Date().toISOString(), ver: 0 };
      a.name = String(b.name ?? a.name ?? "").slice(0, 120);
      if (typeof b.disabled === "boolean") {
        if (me.email === email && b.disabled) return json({ error: "You cannot pause your own account." }, 400);
        if (b.disabled && !a.disabled) a.ver = (a.ver || 0) + 1;
        a.disabled = b.disabled;
      }
      let inviteUrl = null;
      if (!a.hash || b.newInvite) {
        // New admin, or a fresh link to reset their password and authenticator.
        if (a.invite?.hash) await members.delete("admin-invites/" + a.invite.hash);
        const token = randomToken();
        a.invite = { hash: await sha256hex(token), expires: Date.now() + INVITE_DAYS * 864e5 };
        await members.set("admin-invites/" + a.invite.hash, email);
        if (a.hash && b.newInvite) { delete a.hash; delete a.salt; delete a.totp; a.ver = (a.ver || 0) + 1; }
        inviteUrl = new URL("/admin/?invite=" + token, url).toString();
      }
      await members.setJSON("admins/" + email, a);
      return json({ ok: true, admin: publicAdmin(a), inviteUrl });
    }
    if (request.method === "DELETE") {
      const email = normEmail(url.searchParams.get("email"));
      if (me.email === email) return json({ error: "You cannot remove your own account." }, 400);
      const a = await members.get("admins/" + email, { type: "json" });
      if (a?.invite?.hash) await members.delete("admin-invites/" + a.invite.hash);
      await members.delete("admins/" + email);
      return json({ ok: true });
    }
  }

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

  return json({ error: "Not found" }, 404);
};

export const config = { path: ["/api/admin/*"] };
