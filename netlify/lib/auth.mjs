// Guilgal International partner logon: shared helpers for the edge gate and the
// serverless functions. Web Crypto only, so it runs in Node and in Deno.
//
// Only one environment variable is required (Netlify > Site configuration > Environment variables):
//   ADMIN_PASSWORD     password for the admin panel
// Optional overrides (normally created automatically and kept in Netlify Blobs):
//   SESSION_SECRET     signs login cookies; otherwise generated on first use (config/session-secret)
//   ADMIN_TOTP_SECRET  authenticator key; otherwise set up on first visit to /admin/ (config/admin-totp)
//
// Data lives in Netlify Blobs:
//   store "members": users/<email>  { email, name, salt, hash, projects: [slugs] | ["*"], ver, disabled, created }
//                    attempts/<key> { n, until }  failed-login counters
//                    config/session-secret, config/admin-totp, config/admin-totp-pending
//   store "briefs":  <slug>          PDF project briefs uploaded from the admin panel

export const PROJECTS = {
  "pumba": "Pumba Copper & Gold",
  "alpha": "Alpha Tantalum & Tin",
  "nizi-baluma": "Nizi–Baluma Gold",
  "ndela-mpaza": "Ndela–Mpaza",
  "hydropower": "Hydropower Projects",
  "tumfa": "Ghana Tumfa Gold",
};

export const USER_COOKIE = "gi_session";
export const ADMIN_COOKIE = "gi_admin";
export const USER_DAYS = 30;
export const ADMIN_HOURS = 2;

const enc = new TextEncoder();

// The members store is passed in by callers so this module has no hard dependency on Netlify Blobs.
let secretCache = null;
export async function sessionSecret(store) {
  const fromEnv = env("SESSION_SECRET");
  if (fromEnv && fromEnv.length >= 16) return fromEnv;
  if (secretCache) return secretCache;
  if (!store) throw new Error("No session secret");
  let v = await store.get("config/session-secret");
  if (!v) {
    v = b64url(crypto.getRandomValues(new Uint8Array(32)));
    await store.set("config/session-secret", v);
    v = (await store.get("config/session-secret")) || v; // if two requests raced, keep the stored one
  }
  return (secretCache = v);
}
export async function adminTotpSecret(store) {
  return env("ADMIN_TOTP_SECRET") || (store ? await store.get("config/admin-totp") : null);
}
export function newTotpSecret() {
  const a = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";
  return [...crypto.getRandomValues(new Uint8Array(32))].map((x) => a[x % 32]).join("");
}
export function totpUri(secret) {
  const label = encodeURIComponent("Guilgal International:admin");
  return `otpauth://totp/${label}?secret=${secret}&issuer=${encodeURIComponent("Guilgal International")}&digits=6&period=30`;
}

export function env(name) {
  const v = globalThis.Netlify?.env?.get?.(name);
  if (v !== undefined && v !== null) return v;
  return typeof process !== "undefined" ? process.env?.[name] : undefined;
}

// ---------- encoding
export function b64url(bytes) {
  let s = "";
  for (const b of new Uint8Array(bytes)) s += String.fromCharCode(b);
  return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
export function fromB64url(str) {
  const s = atob(str.replace(/-/g, "+").replace(/_/g, "/") + "===".slice((str.length + 3) % 4));
  return Uint8Array.from(s, (c) => c.charCodeAt(0));
}
function hex(bytes) {
  return [...new Uint8Array(bytes)].map((b) => b.toString(16).padStart(2, "0")).join("");
}
export function safeEqual(a, b) {
  if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length) return false;
  let d = 0;
  for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return d === 0;
}

// ---------- passwords (PBKDF2-SHA256)
const ITER = 210000;
export async function hashPassword(password, saltHex) {
  const salt = saltHex ? Uint8Array.from(saltHex.match(/../g).map((h) => parseInt(h, 16))) : crypto.getRandomValues(new Uint8Array(16));
  const key = await crypto.subtle.importKey("raw", enc.encode(password), "PBKDF2", false, ["deriveBits"]);
  const bits = await crypto.subtle.deriveBits({ name: "PBKDF2", hash: "SHA-256", salt, iterations: ITER }, key, 256);
  return { salt: hex(salt), hash: hex(bits) };
}
export async function checkPassword(password, user) {
  if (!user?.salt || !user?.hash) return false;
  const { hash } = await hashPassword(password, user.salt);
  return safeEqual(hash, user.hash);
}
export function randomPassword(len = 14) {
  const chars = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789";
  const r = crypto.getRandomValues(new Uint8Array(len));
  return [...r].map((x) => chars[x % chars.length]).join("");
}

// ---------- signed cookies
async function hmac(secret, data, algo = "SHA-256") {
  const key = await crypto.subtle.importKey("raw", typeof secret === "string" ? enc.encode(secret) : secret, { name: "HMAC", hash: algo }, false, ["sign"]);
  return new Uint8Array(await crypto.subtle.sign("HMAC", key, typeof data === "string" ? enc.encode(data) : data));
}
export async function sign(payload, store) {
  const secret = await sessionSecret(store);
  const body = b64url(enc.encode(JSON.stringify(payload)));
  return body + "." + b64url(await hmac(secret, body));
}
export async function verify(token, store) {
  if (!token || !token.includes(".")) return null;
  let secret;
  try { secret = await sessionSecret(store); } catch { return null; }
  const [body, sig] = token.split(".");
  if (!safeEqual(sig, b64url(await hmac(secret, body)))) return null;
  try {
    const p = JSON.parse(new TextDecoder().decode(fromB64url(body)));
    return p.x && p.x > Date.now() ? p : null;
  } catch {
    return null;
  }
}
export function readCookie(request, name) {
  const all = request.headers.get("cookie") || "";
  for (const part of all.split(/;\s*/)) {
    const i = part.indexOf("=");
    if (i > 0 && part.slice(0, i) === name) return decodeURIComponent(part.slice(i + 1));
  }
  return null;
}
export function cookie(name, value, { maxAge, path = "/", sameSite = "Lax" } = {}) {
  const parts = [`${name}=${encodeURIComponent(value)}`, `Path=${path}`, "HttpOnly", "Secure", `SameSite=${sameSite}`];
  if (maxAge !== undefined) parts.push(`Max-Age=${maxAge}`);
  return parts.join("; ");
}

// ---------- TOTP (RFC 6238, SHA-1, 30 s, 6 digits)
function base32(str) {
  const a = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";
  let bits = "";
  for (const c of str.replace(/[\s=-]/g, "").toUpperCase()) {
    const v = a.indexOf(c);
    if (v < 0) throw new Error("bad base32");
    bits += v.toString(2).padStart(5, "0");
  }
  return Uint8Array.from(bits.match(/.{8}/g) || [], (b) => parseInt(b, 2));
}
export async function totp(secret, t = Date.now(), step = 30) {
  const counter = Math.floor(t / 1000 / step);
  const msg = new Uint8Array(8);
  new DataView(msg.buffer).setBigUint64(0, BigInt(counter));
  const h = await hmac(base32(secret), msg, "SHA-1");
  const o = h[h.length - 1] & 15;
  const n = ((h[o] & 127) << 24) | (h[o + 1] << 16) | (h[o + 2] << 8) | h[o + 3];
  return String(n % 1000000).padStart(6, "0");
}
export async function checkTotp(secret, code) {
  if (!secret || !/^\d{6}$/.test(code || "")) return false;
  const now = Date.now();
  for (const drift of [-30000, 0, 30000]) if (safeEqual(await totp(secret, now + drift), code)) return true;
  return false;
}

// ---------- users
export function normEmail(e) {
  return String(e || "").trim().toLowerCase();
}
export function canSee(user, slug) {
  if (!user || user.disabled) return false;
  const p = user.projects || [];
  return p.includes("*") || p.includes(slug);
}
export function publicUser(u) {
  return { email: u.email, name: u.name || "", projects: u.projects || [], disabled: !!u.disabled, created: u.created || null, lastLogin: u.lastLogin || null };
}

// Session payload: { e: email, v: user.ver, x: expiry ms }. Bumping user.ver (password
// reset, disable) signs every existing session out.
export async function userFromRequest(request, store) {
  const s = await verify(readCookie(request, USER_COOKIE), store);
  if (!s?.e) return null;
  const user = await store.get("users/" + s.e, { type: "json" });
  if (!user || user.disabled || (user.ver || 0) !== s.v) return null;
  return user;
}
export async function isAdmin(request, store) {
  const s = await verify(readCookie(request, ADMIN_COOKIE), store);
  return !!(s && s.a === 1);
}

// Failed-login throttle: 8 failures locks the key for 15 minutes.
export async function throttled(store, key) {
  const a = await store.get("attempts/" + key, { type: "json" });
  return !!(a && a.until && a.until > Date.now());
}
export async function recordFailure(store, key) {
  const a = (await store.get("attempts/" + key, { type: "json" })) || { n: 0 };
  a.n = (a.n || 0) + 1;
  if (a.n >= 8) { a.until = Date.now() + 15 * 60 * 1000; a.n = 0; }
  await store.setJSON("attempts/" + key, a);
}
export async function clearFailures(store, key) {
  await store.delete("attempts/" + key);
}

export function json(data, status = 200, headers = {}) {
  return new Response(JSON.stringify(data), { status, headers: { "Content-Type": "application/json", "Cache-Control": "no-store", ...headers } });
}
