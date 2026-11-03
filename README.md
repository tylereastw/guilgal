# Guilgal International — homepage

Static HTML/CSS/JS built to John's 30 October mock-up and the wording in
"Week 1 Pages, John's Structure". Open `index.html`; no build step.

Sections: header · hero · highlight strip · who we are · our projects (six cards, Partner
access → login) · our approach · latest news & milestones (CMS) · partner with Guilgal
International · footer.

## Still to supply / wire up
- **Logo** — the wordmark in the header and footer is a stand-in for the official
  Guilgal International logo (31 October logo pack).
- **Hero photo** — `public/images/site-openpit.jpg` stands in for John's drilling-at-sunrise
  photo; swap the `src` in the hero.
- **Project card photos** — the three crops (`site-geologists.jpg`, `site-plant.jpg`,
  `site-openpit.jpg`) are taken from the focus triptych and repeat across the six cards;
  replace with one mine-site photo per project.
- **Ndela–Mpaza country** — shown as `[Confirm country]` until confirmed.
- **News** — the three cards are the CMS slots; the first uses the launch-day post title.
- **Links** — `/about/`, `/projects/`, `/investors/#enquiry`, `/news/`, `/contact/`,
  `/partners/login/`, `/privacy/`, `/legal/` are the planned URLs.
- **QR** — `public/images/qr-projects.svg` encodes https://www.guilgal.org/projects/;
  regenerate if the final URL differs.

Fonts (DM Serif Display, DM Sans) are self-hosted in `assets/fonts/`; the page makes no
external requests.
