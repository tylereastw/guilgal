// POST /api/login  { email, password }  -> sets the partner session cookie
// POST /api/logout                       -> clears it
// GET  /api/me                            -> { email, name, projects } for the portal
import { getStore } from "@netlify/blobs";
import { normEmail, checkPassword, sign, cookie, json, userFromRequest, throttled, recordFailure, clearFailures, USER_COOKIE, USER_DAYS, PROJECTS } from "../lib/auth.mjs";

export default async (request, context) => {
  const store = getStore({ name: "members", consistency: "strong" });
  const path = new URL(request.url).pathname;

  if (path === "/api/me") {
    const user = await userFromRequest(request, store);
    if (!user) return json({ error: "Not signed in" }, 401);
    const projects = (user.projects || []).includes("*") ? Object.keys(PROJECTS) : user.projects || [];
    return json({ email: user.email, name: user.name || "", projects });
  }

  if (request.method !== "POST") return json({ error: "Method not allowed" }, 405);

  if (path === "/api/logout") {
    return json({ ok: true }, 200, { "Set-Cookie": cookie(USER_COOKIE, "", { maxAge: 0 }) });
  }

  let body;
  try { body = await request.json(); } catch { return json({ error: "Invalid request" }, 400); }
  const email = normEmail(body.email);
  const password = String(body.password || "");
  const ip = context.ip || "unknown";
  if (!email || !password) return json({ error: "Enter your email and password." }, 400);
  if (await throttled(store, "u:" + email) || await throttled(store, "ip:" + ip)) {
    return json({ error: "Too many attempts. Please wait 15 minutes and try again." }, 429);
  }
  const user = await store.get("users/" + email, { type: "json" });
  const ok = user && !user.disabled && (await checkPassword(password, user));
  if (!ok) {
    await recordFailure(store, "u:" + email);
    await recordFailure(store, "ip:" + ip);
    return json({ error: "That email and password do not match an active account." }, 401);
  }
  await clearFailures(store, "u:" + email);
  user.lastLogin = new Date().toISOString();
  await store.setJSON("users/" + email, user);
  const token = await sign({ e: email, v: user.ver || 0, x: Date.now() + USER_DAYS * 864e5 }, store);
  return json({ ok: true }, 200, { "Set-Cookie": cookie(USER_COOKIE, token, { maxAge: USER_DAYS * 86400 }) });
};

export const config = { path: ["/api/login", "/api/logout", "/api/me"] };
