# Guilgal International website

**Design v2** follows John Boardman's mock-ups (Website Design Handover, 30 October). The previous editorial design is archived in `archive/editorial-v1/` (open its `index.html` via a local server). Image list and sizes: `public/images/v2/IMAGES.md`.

Static, multi-page corporate site for Guilgal International, a trading name of Britcom Trading Limited (registered in England and Wales, company number 15625520).
No framework. Pages are generated from one script so the header, footer and design system stay
consistent:

```bash
python3 tools/build.py
```

Edit content in the data blocks at the top of `tools/build.py` (projects, news, approach steps,
navigation), run the script, and commit the generated `index.html` files. To preview locally,
serve the folder (links use clean URLs such as `about/`):

```bash
python3 -m http.server 8000
```

## Pages
| URL | Page |
|---|---|
| `/` | Home: hero with QR code, highlight strip, Advancing Africa's Mineral Opportunities, Our Projects, Our Approach, Latest News & Milestones, partner call to action |
| `/about/` | About, including What We Do, Focus Minerals, geographic focus, Our Approach, Our Name, closing banner |
| `/about/team/` | Meet the Team |
| `/investors/` | Why Partner with Guilgal International, enquiry form |
| `/news/` | News & Milestones feed, filterable by type (News, Insights) and by project; subscribe box |
| `/contact/` | Enquiry form and john@guilgal.org |
| `/members/` | Partner sign-in (placeholder) |
| `/members/projects/<slug>/` | Private project page template, one per project |
| `/privacy/`, `/cookies/`, `/terms/` | Legal pages (text to be supplied) |

## Before launch
- **Members area needs real access control.** The private project pages carry
  `noindex, nofollow`, are excluded from `sitemap.xml` and disallowed in `robots.txt`, so search
  engines will not list them. That is not security: anyone with the URL can open them. Put
  `/members/` behind the hosting platform's login (for example Wix Members or Netlify Identity)
  before adding any project detail.
- **Forms are not connected.** All forms validate in the browser. Add each form's handler URL as
  `data-endpoint="..."` on the `<form>` (in `tools/build.py`); until then they ask visitors to email
  john@guilgal.org.
- **John Boardman's photo** goes at `public/images/team/john-boardman.jpg` (portrait, 4:5). His
  biography, and Gedeon's title and biography, are placeholders.
- **News:** the cards are "Coming soon" placeholders until the first posts are published.
- **Our Approach:** the heading and four steps are placeholder test copy (Lorem ipsum) until the final wording is agreed; edit `APPROACH` and the heading in `tools/build.py`.
- **Project pages:** overview, licence and location, geology, work completed and next steps are
  placeholders. The Download Project Brief button is disabled until a brief exists. The hydropower
  page states that Guilgal International's role is commercial facilitation and introductions only.
- **Legal pages:** Privacy, Cookies and Terms text to be supplied by the company's advisers.
- **Photography:** project card photos and inner-page heroes reuse the supplied artwork; replace
  with project and field photography when available (`public/images/project-*.jpg`).
- **QR code:** `public/images/qr-projects.svg` points to https://www.guilgal.org/projects/.

## Writing rules
British English, no em dashes, always "Guilgal International". Guilgal International is a
facilitator and consultant, not an operator, broker, fund, adviser or lender. No invented phone
numbers, addresses, credentials, timelines, figures, tonnages, grades or ownership splits. The
build script refuses to write a page containing an em dash.

## Design
Forest green `#10291F` / `#13251D`, muted gold `#D7B46E`, cream `#F6F3EB`, white. Sections meet
along an open-pit rock cut. Gold is used for decoration and on dark backgrounds; text on cream
uses dark green for contrast.

## Fonts
Design v2 uses self-hosted Montserrat (headings, UI), Oswald (card labels), Open Sans (body) and Cinzel (wordmark), all SIL Open Font License, in `assets/fonts/v2/`. The earlier request for **Canela** (headings) and **Neue Haas Grotesk Text** (body, navigation, UI).
Both are commercial typefaces that need a web licence and are not included. `css/fonts.css`
declares them; they load once the WOFF2 files are placed in `assets/fonts/licensed/` (names in
the README there). Until then the site uses the self-hosted DM Serif Display / DM Sans pair. No
fonts are loaded from third parties.

## Partner logon and admin (Netlify)

Project pages live under `/members/` and are private. Each partner has their own email and
password and sees only the projects assigned to them. Sessions last 30 days. Project pages are
reached by direct link (or QR code); there is no public projects page.

| Piece | File |
|---|---|
| Gate on every `/members/` request (redirects to `/login/`, blocks unassigned projects) | `netlify/edge-functions/members-gate.mjs` |
| Partner sign in / sign out / who am I | `netlify/functions/login.mjs` (`/api/login`, `/api/logout`, `/api/me`) |
| Admin API: partners, project access, briefs | `netlify/functions/admin.mjs` (`/api/admin/*`) |
| Project briefs: PDF generated from each project page at build time (`members/projects/<slug>/brief.pdf`, behind the login) | `tools/build.py` + `tools/briefs.mjs` |
| Shared crypto and session helpers | `netlify/lib/auth.mjs` |
| Pages | `/login/`, `/members/` (portal), `/admin/` |

Data (partner accounts, uploaded briefs) is stored in Netlify Blobs; no database to run.

**One-off setup**
1. In Netlify, Site configuration > Environment variables, add `ADMIN_PASSWORD` (scope:
   Functions) and redeploy. That is the only variable needed.
2. Open `/admin/` on the site. The first visit shows a setup screen: enter the admin password,
   scan the QR code with an authenticator app (Google Authenticator, Microsoft Authenticator,
   1Password), and type the 6-digit code it shows. From then on, admin sign-in is the password
   plus the current code.

The cookie signing secret and the authenticator key are generated and stored automatically in
Netlify Blobs. Optional overrides: `SESSION_SECRET` and `ADMIN_TOTP_SECRET` environment
variables (`tools/admin_totp.py` can create a key). To reset the authenticator (for example a
lost phone), delete the `config/admin-totp` entry in the `members` blob store from the Netlify
dashboard (Blobs) and visit `/admin/` again.

**In the admin panel** you can add a partner (email, name, projects; a password is generated
and shown once), change their projects, reset their password (signs them out everywhere),
disable or delete them, preview each project's generated brief, and download each project's QR
code and link to send on. After adding a partner the panel shows their login details to copy or email.


### More admins

Sign in to `/admin/` and open the **Admins** tab. Enter the person's email and name and click
**Create set-up link**, then send them the link (Copy link or Open email draft). It works once and
expires in 7 days. They choose their own password (at least 12 characters) and scan their own
authenticator QR code. Afterwards they sign in with email, password and code. The main admin
(ADMIN_PASSWORD, email left blank) always keeps access. From the Admins tab you can pause,
resume, reset (new set-up link) or remove any other admin.

## Forms
The contact and investor enquiry forms are Netlify Forms (`data-netlify`, with a honeypot).
Submissions appear in Netlify under Forms; turn on email notifications there
(Forms > Form notifications) so they reach john@guilgal.org.

## Images
`public/images/v2/IMAGES.md` lists every image; `public/images/v2/IMAGE_PROMPTS.md` lists the
blurry ones with prompts to regenerate them.

## Cookies and analytics
Microsoft Clarity (project `z8gzw297n1`) loads only after a visitor chooses "Accept analytics" in
the cookie banner (`js/consent.js`), and never on `/members/`, `/login/` or `/admin/`, so private
project pages are not recorded. "Cookie settings" in the footer reopens the banner. The Cookie
Policy page lists every cookie. Netlify hosting and Forms set no analytics cookies; Netlify
Analytics, if switched on in the dashboard, is server-side and cookie-free.

## Building
`python3 tools/build.py` regenerates every page and then prints the project brief PDFs with
Playwright (`node tools/briefs.mjs`). Commit the generated files.
