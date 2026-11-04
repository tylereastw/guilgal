// Netlify build step: copy only the website files into dist/, which is what gets published.
// Source and tooling (tools/, netlify/, package.json, README and other notes) stay private.
// Run locally with: node tools/stage.mjs
import { cpSync, mkdirSync, rmSync, existsSync, statSync } from "node:fs";
import { join, dirname, extname, basename } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const out = join(root, "dist");

// Everything the site serves. Anything not listed here is never published.
const PUBLISH = [
  "index.html", "favicon.ico", "robots.txt", "sitemap.xml",
  "about", "admin", "archive", "assets", "contact", "cookies", "css", "investors", "js",
  "login", "members", "privacy", "public", "terms", "thanks",
];
// Never published, even inside the folders above.
const SKIP_EXT = new Set([".md", ".py", ".mjs", ".ts", ".map", ".psd", ".ai"]);
const SKIP_NAMES = new Set(["package.json", "package-lock.json", ".DS_Store", "Thumbs.db"]);

if (existsSync(out)) rmSync(out, { recursive: true, force: true });
mkdirSync(out, { recursive: true });

let copied = 0;
for (const entry of PUBLISH) {
  const src = join(root, entry);
  if (!existsSync(src)) continue;
  cpSync(src, join(out, entry), {
    recursive: true,
    filter: s => {
      if (statSync(s).isDirectory()) return !basename(s).startsWith(".");
      const keep = !SKIP_EXT.has(extname(s).toLowerCase()) && !SKIP_NAMES.has(basename(s)) && !basename(s).startsWith(".");
      if (keep) copied++;
      return keep;
    },
  });
}
console.log(`staged ${copied} files into dist/`);
