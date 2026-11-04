// GET /members/projects/<slug>/brief  -> the project's PDF brief, for signed-in partners
// with access to that project. Briefs are uploaded from the admin panel.
import { getStore } from "@netlify/blobs";
import { userFromRequest, canSee, PROJECTS } from "../lib/auth.mjs";

export default async (request, context) => {
  const slug = context.params?.slug || new URL(request.url).pathname.split("/")[3];
  if (!PROJECTS[slug]) return new Response("Not found", { status: 404 });
  const user = await userFromRequest(request, getStore({ name: "members", consistency: "strong" }));
  if (!user || !canSee(user, slug)) return new Response("Forbidden", { status: 403 });
  const briefs = getStore({ name: "briefs", consistency: "strong" });
  const file = await briefs.getWithMetadata(slug, { type: "arrayBuffer" });
  if (!file) {
    return new Response(`<!doctype html><meta charset="utf-8"><title>Brief not available</title><body style="font-family:Arial,sans-serif;padding:60px 20px;text-align:center">
<h1 style="font-size:1.4rem">The ${PROJECTS[slug]} brief is not available yet</h1><p>Please contact <a href="mailto:john@guilgal.org">john@guilgal.org</a>.</p>
<p><a href="/members/projects/${slug}/">Back to the project</a></p></body>`, { status: 404, headers: { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" } });
  }
  const name = (file.metadata?.filename || `Guilgal-International-${slug}-brief.pdf`).replace(/[^\w.\- ]/g, "");
  return new Response(file.data, { headers: {
    "Content-Type": file.metadata?.type || "application/pdf",
    "Content-Disposition": `attachment; filename="${name}"`,
    "Cache-Control": "private, no-store",
    "X-Robots-Tag": "noindex, nofollow, noarchive",
  } });
};

export const config = { path: "/members/projects/:slug/brief" };
