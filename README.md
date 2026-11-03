# Guilgal International website

Static, multi-page corporate site for Guilgal International Ltd (registered in England and Wales).
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
| `/projects/` | Six public project cards (name, country, mineral only) with Partner Access |
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
  biography, and Gedeon's and Didier's titles and biographies, are placeholders.
- **News:** the three news posts are the sample posts from the approved mock-up and need
  confirming or replacing; summaries and the Insights guide are placeholders.
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
Specified pairing: **Canela** (headings) and **Neue Haas Grotesk Text** (body, navigation, UI).
Both are commercial typefaces that need a web licence and are not included. `css/fonts.css`
declares them; they load once the WOFF2 files are placed in `assets/fonts/licensed/` (names in
the README there). Until then the site uses the self-hosted DM Serif Display / DM Sans pair. No
fonts are loaded from third parties.
