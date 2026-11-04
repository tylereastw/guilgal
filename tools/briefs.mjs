// Print each project's brief.html (written by tools/build.py) to brief.pdf with Chromium.
// Run automatically at the end of `python3 tools/build.py`, or on its own:
//   node tools/briefs.mjs
// Needs Playwright: npm install --no-save playwright && npx playwright install chromium
import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { existsSync, readdirSync } from "node:fs";
import { extname, join, normalize, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const TYPES = { ".html": "text/html", ".css": "text/css", ".jpg": "image/jpeg", ".png": "image/png", ".svg": "image/svg+xml", ".woff2": "font/woff2" };

let chromium;
try { ({ chromium } = createRequire(import.meta.url)("playwright")); }
catch { console.error("Playwright is not installed; project brief PDFs were not regenerated."); process.exit(0); }

// tiny static server so fonts and images load exactly as on the site
const server = createServer(async (req, res) => {
  const path = normalize(decodeURIComponent(new URL(req.url, "http://x").pathname)).replace(/^(\.\.[/\\])+/, "");
  try { res.writeHead(200, { "Content-Type": TYPES[extname(path)] || "application/octet-stream" }); res.end(await readFile(join(ROOT, path))); }
  catch { res.writeHead(404); res.end(); }
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const base = `http://127.0.0.1:${server.address().port}`;

const dir = join(ROOT, "members", "projects");
const slugs = readdirSync(dir).filter((s) => existsSync(join(dir, s, "brief.html")));
const browser = await chromium.launch();
const page = await browser.newPage();
for (const slug of slugs) {
  await page.goto(`${base}/members/projects/${slug}/brief.html`, { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: join(dir, slug, "brief.pdf"), format: "A4", printBackground: true, preferCSSPageSize: true });
  console.log("brief:", slug);
}
await browser.close();
server.close();
