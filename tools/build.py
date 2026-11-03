#!/usr/bin/env python3
"""Build the Guilgal International static site.

Every page shares one header, footer and design system. Content lives in the
data blocks below; run `python3 tools/build.py` from the repository root after
editing and commit the generated HTML.

Writing rules (from the brief): British English, no em dashes, always
"Guilgal International", no invented phone numbers, addresses, credentials,
timelines, financial figures, tonnages, grades or ownership splits.
"""
from html import escape
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
SITE_URL = "https://www.guilgal.org"
EMAIL = "john@guilgal.org"

# ---------------------------------------------------------------- data
PROJECTS = [
    # slug, name, country, mineral line, card image
    ("pumba", "Pumba Copper & Gold", "DRC", "Copper & Gold", "project-openpit.jpg"),
    ("alpha", "Alpha Tantalum & Tin", "DRC", "Tantalum & Tin", "project-plant.jpg"),
    ("ndela-mpaza", "Ndela–Mpaza", "DRC", "Critical Minerals", "project-geologists.jpg"),
    ("nizi-baluma", "Nizi–Baluma Gold", "DRC", "Gold", "project-rock.jpg"),
    ("tumfa", "Tumfa Gold", "Ghana", "Gold", "project-forest.jpg"),
    ("hydropower", "Hydropower & Infrastructure", "DRC", "Energy & Infrastructure", "project-valley.jpg"),
]
PROJECT_NAMES = {p[0]: p[1] for p in PROJECTS}

# News & Milestones. The three news items are the sample posts from the approved
# mock-up; replace or confirm them before launch. `project` links a post to a
# project's milestone list (None = company news).
NEWS = [
    dict(date="2026-10-30", label="30 Oct 2026", kind="news", project=None, image="news-1.jpg",
         alt="Terraced open-pit mine",
         title="Guilgal International Advances DRC Project Portfolio",
         summary="[Article summary to be supplied]"),
    dict(date="2026-10-22", label="22 Oct 2026", kind="news", project="tumfa", image="news-2.jpg",
         alt="Forested hills above the mist",
         title="Strategic Partnership Discussions Underway in Ghana",
         summary="[Article summary to be supplied]"),
    dict(date="2026-10-14", label="14 Oct 2026", kind="news", project=None, image="news-3.jpg",
         alt="Mountains at sunset",
         title="Portfolio Update: Progress and Next Steps",
         summary="[Article summary to be supplied]"),
    dict(date="", label="Insights", kind="insight", project=None, image="project-valley.jpg",
         alt="Misty forested hills",
         title="[Insight guide title to be supplied]",
         summary="Educational guides on mineral projects and partnerships in Africa will be published here."),
]

APPROACH = [  # John Boardman's wording (Week 1 structure, About page)
    ("Identify", "Source and review promising project opportunities."),
    ("Evaluate", "Coordinate geological, technical and commercial assessment."),
    ("Partner", "Bring together project owners, specialists and strategic partners."),
    ("Develop", "Support progress towards structured, responsible and commercially viable outcomes."),
]

NAV = [
    ("Home", ""),
    ("About", "about/", [("About Guilgal International", "about/"), ("Our Name", "about/#our-name"), ("Meet the Team", "about/team/")]),
    ("Projects", "projects/"),
    ("Investors", "investors/"),
    ("News & Milestones", "news/"),
    ("Contact", "contact/"),
]

RIDGE = (ROOT / "tools" / "ridge.txt").read_text().split("\n")
RIDGE_CREST, RIDGE_FILL = RIDGE[0], RIDGE[1]

DISCLAIMER = ("Guilgal International does not provide investment, financial or legal advice. "
              "Nothing on this site is an offer or solicitation.")


# ---------------------------------------------------------------- pieces
def e(s):
    return escape(s, quote=True)


def logo(p, small=False):
    cls = "logo logo--small" if small else "logo"
    return f'''<a class="{cls}" href="{p}" aria-label="Guilgal International home">
      <svg class="logo__mark" viewBox="0 0 80 24" aria-hidden="true"><path d="M2 22 L26 6 L34 12 L48 2 L78 22" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"/></svg>
      <span class="logo__name">GUILGAL INTERNATIONAL</span>
      <span class="logo__tag">EXPLORATION | DEVELOPMENT | PARTNERSHIPS</span>
    </a>'''


def header(p, active):
    items = []
    for item in NAV:
        label, href = item[0], item[1]
        cur = ' aria-current="page"' if label == active else ""
        if len(item) == 3:
            sub = "".join(f'<li><a href="{p}{h}">{e(l)}</a></li>' for l, h in item[2])
            items.append(f'''<li class="nav__item nav__item--has-sub">
          <a href="{p}{href}"{cur}>{e(label)}</a>
          <button class="nav__subtoggle" aria-expanded="false" aria-label="Show About pages"><i></i></button>
          <ul class="nav__sub">{sub}</ul>
        </li>''')
        else:
            items.append(f'<li class="nav__item"><a href="{p}{href}"{cur}>{e(label)}</a></li>')
    return f'''<header class="nav" id="top">
    {logo(p)}
    <nav class="nav__links" id="menu" aria-label="Main">
      <ul class="nav__list">
        {"".join(items)}
      </ul>
      <a class="btn btn--outline nav__cta" href="{p}investors/#enquiry">Investor Enquiries</a>
    </nav>
    <button class="burger" aria-expanded="false" aria-controls="menu" aria-label="Menu"><span></span><span></span><span></span></button>
  </header>'''


def footer(p):
    links = "".join(f'<a href="{p}{n[1]}">{e(n[0])}</a>' for n in NAV[1:])
    return f'''<footer class="footer">
    <div class="wrap footer__top">
      <div class="footer__brand">
        {logo(p, small=True)}
        <p class="footer__lines">Mining • Critical Minerals • Project Development • Strategic Partnerships</p>
        <p class="footer__motto">Connecting Opportunities. Developing Partnerships.</p>
      </div>
      <nav class="footer__nav" aria-label="Footer">{links}<a href="mailto:{EMAIL}">{EMAIL}</a></nav>
    </div>
    <div class="wrap footer__bottom">
      <p class="footer__disclaimer">{DISCLAIMER}</p>
      <p class="footer__legal">Guilgal International Ltd, registered in England and Wales. <a href="{p}privacy/">Privacy</a> · <a href="{p}cookies/">Cookies</a> · <a href="{p}terms/">Terms</a></p>
    </div>
  </footer>'''


def ridge_svg(cls="ridge"):
    return f'''<svg class="{cls}" viewBox="0 0 1440 200" preserveAspectRatio="none" aria-hidden="true">
        <path class="ridge__fill" d="{RIDGE_FILL}"/>
        <path class="ridge__glow" d="{RIDGE_CREST}"/>
        <path class="ridge__line" d="{RIDGE_CREST}"/>
      </svg>'''


def page(path, title, description, active, body, p, noindex=False, extra_head=""):
    robots = '\n  <meta name="robots" content="noindex, nofollow, noarchive">' if noindex else ""
    canonical = "" if noindex else f'\n  <link rel="canonical" href="{SITE_URL}/{path}">'
    html = f'''<!doctype html>
<html lang="en-GB">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(title)}</title>
  <meta name="description" content="{e(description)}">{robots}{canonical}
  <link rel="preload" href="{p}assets/fonts/DMSerifDisplay-normal-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="{p}assets/fonts/DMSans-normal-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="{p}css/fonts.css">
  <link rel="stylesheet" href="{p}css/styles.css">{extra_head}
</head>
<body>
  <a class="skip" href="#main">Skip to main content</a>
  {header(p, active)}
  <svg width="0" height="0" style="position:absolute" aria-hidden="true"><filter id="glow" x="-5%" y="-100%" width="110%" height="300%"><feGaussianBlur stdDeviation="4"/></filter></svg>

  <main id="main">
{body}
  </main>

  {footer(p)}

  <script src="{p}js/main.js"></script>
</body>
</html>
'''
    assert "—" not in html, f"em dash found in {path}"
    out = ROOT / path / "index.html" if path else ROOT / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    return out


def page_hero(p, image, title, intro="", eyebrow=""):
    eb = f'<p class="eyebrow">{e(eyebrow)}</p>' if eyebrow else ""
    it = f'<p class="page-hero__intro">{intro}</p>' if intro else ""
    return f'''    <section class="page-hero">
      <div class="page-hero__bg"><img src="{p}public/images/{image}" alt=""></div>
      <div class="page-hero__tint"></div>
      <div class="wrap page-hero__text">
        {eb}
        <h1>{title}</h1>
        {it}
      </div>
      {ridge_svg()}
    </section>
'''


def project_cards(p, heading_level="h3"):
    cards = []
    for slug, name, country, mineral, img in PROJECTS:
        cards.append(f'''<li class="pcard">
            <div class="pcard__photo"><img src="{p}public/images/{img}" alt="" loading="lazy"></div>
            <div class="pcard__body">
              <{heading_level}>{e(name)}</{heading_level}>
              <p class="pcard__meta"><span>{e(country)}</span><span>{e(mineral)}</span></p>
              <a class="btn btn--small" href="{p}members/projects/{slug}/" rel="nofollow">Partner Access <i class="arr"></i></a>
            </div>
          </li>''')
    return '<ul class="pcards">' + "".join(cards) + "</ul>"


def news_card(p, n):
    t = f'<time datetime="{n["date"]}">{e(n["label"])}</time>' if n["date"] else f'<span class="news__kind">{e(n["label"])}</span>'
    proj = n["project"] or ""
    return f'''<li class="news__card" data-kind="{n["kind"]}" data-project="{proj}">
            <a href="{p}news/">
              <div class="news__photo"><img src="{p}public/images/{n["image"]}" alt="{e(n["alt"])}" loading="lazy"></div>
              <div class="news__body">{t}<h3>{e(n["title"])}</h3><i class="arr"></i></div>
            </a>
          </li>'''


def approach_section(p):
    steps = "".join(
        f'<li><span class="path__num">{i:02d}</span><h3>{t}</h3><p>{d}</p></li>'
        for i, (t, d) in enumerate(APPROACH, 1))
    return f'''    <section class="path" id="approach">
      {ridge_svg("ridge ridge--top")}
      <div class="wrap">
        <div class="path__head">
          <h2>Our <em>Approach</em></h2>
          <p>Identify · Evaluate · Partner · Develop</p>
        </div>
        <ol class="path__steps">{steps}</ol>
        <a class="link path__link" href="{p}about/#approach">How we work <i class="arr"></i></a>
      </div>
      {ridge_svg("ridge ridge--bottom")}
    </section>
'''

def consent(name="consent"):
    return f'''<label class="consent"><input type="checkbox" name="{name}" required><span>I agree that Guilgal International may store and process the details in this form to respond to my enquiry. See the <a href="PRIVACY">Privacy Policy</a>.*</span></label>'''


def form_status():
    return '<p class="form__msg" role="alert" hidden></p>'


# ---------------------------------------------------------------- pages
def home():
    p = ""
    latest = [n for n in NEWS if n["kind"] == "news"][:3]
    body = f'''    <!-- ================= HERO ================= -->
    <section class="hero">
      <div class="hero__stage">
        <div class="hero__bg"><img src="public/images/guilgal_hero_background_1920x1080.png" alt="Sunset over mountains and misty forested hills in Central Africa"></div>
        <div class="hero__tint"></div>
        <div class="hero__map" aria-hidden="true"><img src="public/images/guilgal_drc_map_layer_mining_2x.png" alt=""></div>
      </div>
      <div class="hero__text">
        <p class="eyebrow">Mineral Exploration &amp; Strategic Development</p>
        <h1>Unlocking<br>Africa's Mineral<br><em>Potential</em></h1>
        <p class="hero__sub">Connecting high-potential mineral projects with technical expertise, development partners and international partnerships.</p>
        <div class="hero__actions">
          <a class="btn btn--gold" href="projects/">Explore Our Projects <i class="arr"></i></a>
          <a class="btn btn--outline" href="investors/#enquiry">Investor Enquiries</a>
        </div>
        <figure class="qr">
          <img src="public/images/qr-projects.svg" alt="QR code linking to the Guilgal International projects page" width="72" height="72">
          <figcaption>Scan to explore our projects</figcaption>
        </figure>
      </div>
      <svg class="contours contours--hero" viewBox="0 0 600 220" preserveAspectRatio="none" aria-hidden="true">
        <path d="M0 200 C120 170 220 210 340 180 S520 150 600 170"/>
        <path d="M60 220 C180 190 260 230 380 200 S540 170 600 190"/>
        <path d="M200 215 C300 195 380 225 480 205 S580 190 600 205"/>
      </svg>
      <div class="hero__rockface" aria-hidden="true"><img src="public/images/news-1.jpg" alt=""></div>
      {ridge_svg()}
    </section>

    <!-- ================= HIGHLIGHT STRIP ================= -->
    <section class="strip ivory" aria-label="Focus areas">
      <ul class="wrap strip__list">
        <li><strong>Copper &amp; Gold</strong><span>Exploration opportunities</span></li>
        <li><strong>Critical Minerals</strong><span>Strategic resources</span></li>
        <li><strong>Strategic Partnerships</strong><span>Lasting value</span></li>
      </ul>
    </section>

    <!-- ================= ADVANCING AFRICA'S MINERAL OPPORTUNITIES ================= -->
    <section class="focus ivory" id="who-we-are">
      <div class="wrap focus__grid">
        <div class="focus__text">
          <h2>Advancing Africa's<br>Mineral<br>Opportunities</h2>
          <span class="rule"></span>
        </div>
        <figure class="focus__panels"><img src="public/images/guilgal_focus_triptych.png" alt="Three angled photographs: geologists surveying a site, a mine with processing plant in the hills, and an open-pit terrace"></figure>
        <div class="focus__quote">
          <p>Guilgal International brings together mineral projects in the Democratic Republic of the Congo, Ghana and across Africa with the technical expertise and international partners needed to move them forward.</p>
          <a class="link link--dark" href="about/">About Guilgal International <i class="arr"></i></a>
        </div>
      </div>
    </section>

    <!-- ================= OUR PROJECTS ================= -->
    <section class="projects ivory" id="projects">
      <div class="wrap">
        <div class="section-head">
          <h2><em>Our Projects</em></h2>
          <p>Six projects across the Democratic Republic of the Congo and Ghana. Full project information is available to invited partners.</p>
        </div>
        {project_cards(p)}
        <p class="projects__more"><a class="link link--dark" href="projects/">Explore Our Projects <i class="arr"></i></a></p>
      </div>
    </section>

{approach_section(p)}
    <!-- ================= LATEST NEWS & MILESTONES ================= -->
    <section class="news ivory" id="news">
      <div class="wrap">
        <div class="news__head">
          <h2><em>Latest News &amp; Milestones</em></h2>
          <a class="link link--dark" href="news/">View all updates <i class="arr"></i></a>
        </div>
        <ul class="news__cards">{"".join(news_card(p, n) for n in latest)}
        </ul>
      </div>
    </section>

    <!-- ================= PARTNER CALL TO ACTION ================= -->
    <section class="approach partner">
      <div class="approach__bg"><img src="public/images/guilgal_approach_natural_mirrored.png" alt=""></div>
      <div class="wrap partner__text">
        <h2>Partner with<br><em>Guilgal International</em></h2>
        <p>We welcome enquiries from mining companies, technical partners, investors and strategic collaborators.</p>
        <div class="hero__actions">
          <a class="btn btn--gold" href="investors/#enquiry">Investor Enquiries <i class="arr"></i></a>
          <a class="btn btn--outline" href="contact/">Contact Us</a>
        </div>
      </div>
    </section>
'''
    page("", "Guilgal International | Unlocking Africa's Mineral Potential",
         "Guilgal International connects high-potential mineral projects in the DRC and Ghana with technical expertise and international partners.",
         "Home", body, p)


def about():
    p = "../"
    cols = [
        ("Project identification", "Sourcing and reviewing promising mineral opportunities with local project owners."),
        ("Technical evaluation", "Coordinating geological, technical and commercial assessment with specialists."),
        ("Partnerships", "Introducing project owners to technical, financial and operational partners."),
        ("Strategic development", "Supporting projects towards structured, responsible and commercially viable outcomes."),
    ]
    cols_html = "".join(f'<li><h3>{e(t)}</h3><p>{e(d)}</p></li>' for t, d in cols)
    minerals = "".join(f"<li>{m}</li>" for m in ["Copper", "Gold", "Tantalum", "Tin", "Critical Minerals"])
    body = page_hero(p, "guilgal_approach_natural_mirrored.png", "People. Projects.<br><em>Partnerships.</em>",
                     "Guilgal International brings together mineral projects in Africa, technical expertise and international partners.") + f'''
    <section class="split ivory" id="who-we-are">
      <div class="wrap split__grid">
        <h2>Advancing Africa's<br>Mineral Opportunities</h2>
        <div>
          <p>Guilgal International is a UK company that brings together mineral projects in the Democratic Republic of the Congo, Ghana and across Africa with the technical expertise and international partners needed to advance them.</p>
          <p>We work as a facilitator and consultant, alongside local project owners, geological specialists, technical consultants and international partners.</p>
        </div>
      </div>
    </section>

    <section class="columns ivory" id="what-we-do">
      <div class="wrap">
        <h2><em>What We Do</em></h2>
        <ul class="columns__list">{cols_html}</ul>
      </div>
    </section>

    <section class="facts facts--light">
      <div class="wrap facts__grid">
        <div>
          <h2>Focus Minerals</h2>
          <ul class="minerals">{minerals}</ul>
        </div>
        <div>
          <h2>Democratic Republic of the Congo <em>and Beyond</em></h2>
          <p>Our primary focus is the Democratic Republic of the Congo, with opportunities in Ghana and selected projects elsewhere in Africa.</p>
          <ul class="places"><li>Democratic Republic of the Congo</li><li>Ghana</li><li>Other African opportunities</li></ul>
        </div>
      </div>
    </section>

{approach_section(p)}
    <section class="name ivory" id="our-name">
      <div class="wrap name__grid">
        <h2>Guilgal: A Name Rooted<br>in <em>New Beginnings</em></h2>
        <div>
          <p>The name Guilgal, the French form of the ancient Hebrew name Gilgal, carries an association with renewal, progress and new beginnings.</p>
          <p>For Guilgal International, these principles reflect our commitment to identifying opportunities, building trusted partnerships and transforming mineral resources and infrastructure potential into sustainable economic development.</p>
          <p class="strapline">Rooted in Africa. Connected Globally.</p>
        </div>
      </div>
    </section>

    <section class="banner">
      <div class="banner__bg"><img src="{p}public/images/guilgal_hero_background_1920x1080.png" alt=""></div>
      <div class="wrap banner__text">
        <h2>A Trusted Partner for <em>Sustainable Growth</em></h2>
        <div class="hero__actions"><a class="btn btn--gold" href="{p}investors/#enquiry">Investor Enquiries <i class="arr"></i></a><a class="btn btn--outline" href="team/">Meet the Team</a></div>
      </div>
    </section>
'''
    page("about/", "About | Guilgal International",
         "Guilgal International brings together mineral projects in the DRC, Ghana and across Africa with technical expertise and international partners.",
         "About", body, p)


def team():
    p = "../../"
    people = [
        ("John Boardman", "Director, Guilgal International", "john-boardman.jpg", "[Biography to be supplied]"),
        ("Gedeon", "Title to be confirmed", None, "Biography to be confirmed."),
        ("Didier", "Title to be confirmed", None, "Biography to be confirmed."),
    ]
    cards = []
    for name, role, img, bio in people:
        photo = (f'<img src="{p}public/images/team/{img}" alt="Portrait of {e(name)}" onerror="this.remove()">' if img else "")
        cards.append(f'''<li class="person">
            <div class="person__photo">{photo}<span class="person__initial" aria-hidden="true">{e(name[0])}</span></div>
            <h2>{e(name)}</h2>
            <p class="person__role">{e(role)}</p>
            <p>{e(bio)}</p>
          </li>''')
    body = page_hero(p, "guilgal_hero_background_1920x1080.png", "Meet the <em>Team</em>",
                     "The people behind Guilgal International.") + f'''
    <section class="team ivory">
      <div class="wrap">
        <ul class="people">{"".join(cards)}</ul>
      </div>
    </section>
'''
    page("about/team/", "Meet the Team | Guilgal International",
         "The people behind Guilgal International.", "About", body, p)


def projects():
    p = "../"
    body = page_hero(p, "guilgal_hero_background_1920x1080.png", "Our <em>Projects</em>",
                     "Six projects across the Democratic Republic of the Congo and Ghana.") + f'''
    <section class="projects ivory">
      <div class="wrap">
        <div class="section-head">
          <h2>Project portfolio</h2>
          <p>Full project pages are private and available to invited partners only. Select Partner Access to sign in, or request access through an investor enquiry.</p>
        </div>
        {project_cards(p, "h2")}
        <div class="notice">
          <p>Partner access is by invitation. <a class="link link--dark" href="{p}investors/#enquiry">Request access <i class="arr"></i></a></p>
        </div>
      </div>
    </section>
'''
    page("projects/", "Projects | Guilgal International",
         "Guilgal International's six mineral and infrastructure projects in the Democratic Republic of the Congo and Ghana.",
         "Projects", body, p)


def enquiry_form(p, with_projects=True):
    opts = "".join(f'<option value="{s}">{e(n)}</option>' for s, n, *_ in PROJECTS)
    area = f'''<label class="field"><span>Area of interest*</span><select name="interest" required><option value="">Select a project</option>{opts}<option value="general">General partnership enquiry</option></select></label>''' if with_projects else ""
    return f'''<form class="form" novalidate data-form>
          <div class="form__row">
            <label class="field"><span>Name*</span><input type="text" name="name" autocomplete="name" required></label>
            <label class="field"><span>Organisation</span><input type="text" name="organisation" autocomplete="organization"></label>
          </div>
          <div class="form__row">
            <label class="field"><span>Email*</span><input type="email" name="email" autocomplete="email" required></label>
            <label class="field"><span>Country</span><input type="text" name="country" autocomplete="country-name"></label>
          </div>
          {area}
          <label class="field"><span>Message*</span><textarea name="message" rows="5" required></textarea></label>
          {consent().replace("PRIVACY", p + "privacy/")}
          {form_status()}
          <button class="btn btn--gold" type="submit">Send enquiry <i class="arr"></i></button>
        </form>'''


def investors():
    p = "../"
    why = [
        ("Vetted opportunities", "Projects are reviewed before they are introduced to partners."),
        ("Local relationships", "Established working relationships with project owners and stakeholders on the ground."),
        ("Technical networks", "Access to geological, technical and commercial specialists."),
        ("Long-term partnerships", "A focus on durable relationships rather than single transactions."),
    ]
    why_html = "".join(f'<li><h3>{e(t)}</h3><p>{e(d)}</p></li>' for t, d in why)
    body = page_hero(p, "guilgal_approach_natural_mirrored.png",
                     "Partner with Guilgal International:<br><em>Unlock the Value of Africa</em>") + f'''
    <section class="columns ivory">
      <div class="wrap">
        <h2>Why Partner with <em>Guilgal International?</em></h2>
        <ul class="columns__list">{why_html}</ul>
      </div>
    </section>

    <section class="enquiry" id="enquiry">
      {ridge_svg("ridge ridge--top")}
      <div class="wrap enquiry__grid">
        <div>
          <h2>Investor <em>Enquiries</em></h2>
          <p>Tell us about your organisation and the projects you are interested in. Access to private project pages is by invitation.</p>
          <p class="small">{DISCLAIMER}</p>
        </div>
        {enquiry_form(p)}
      </div>
    </section>
'''
    page("investors/", "Investors | Guilgal International",
         "Partner with Guilgal International on mineral projects in the Democratic Republic of the Congo and Ghana.",
         "Investors", body, p)


def news():
    p = "../"
    proj_opts = "".join(f'<option value="{s}">{e(n)}</option>' for s, n, *_ in PROJECTS)
    body = page_hero(p, "guilgal_hero_background_1920x1080.png", "News &amp; <em>Milestones</em>",
                     "Company news, project milestones and insights from Guilgal International.") + f'''
    <section class="news news--page ivory">
      <div class="wrap">
        <div class="filters" role="group" aria-label="Filter updates">
          <div class="filters__kinds">
            <button type="button" class="chip is-on" data-kind="all" aria-pressed="true">All</button>
            <button type="button" class="chip" data-kind="news" aria-pressed="false">News</button>
            <button type="button" class="chip" data-kind="insight" aria-pressed="false">Insights</button>
          </div>
          <label class="filters__project"><span>Project</span><select data-project-filter><option value="">All projects</option>{proj_opts}</select></label>
        </div>
        <ul class="news__cards" data-feed>{"".join(news_card(p, n) for n in NEWS)}
        </ul>
        <p class="feed__empty" hidden>No updates for this selection yet.</p>
      </div>
    </section>

    <section class="subscribe">
      {ridge_svg("ridge ridge--top")}
      <div class="wrap subscribe__grid">
        <div>
          <h2>Stay <em>Informed</em></h2>
          <p>Receive news and milestones from Guilgal International by email.</p>
        </div>
        <form class="form form--inline" novalidate data-form>
          <label class="field"><span>Email*</span><input type="email" name="email" autocomplete="email" required></label>
          {consent("subscribe_consent").replace("PRIVACY", p + "privacy/")}
          {form_status()}
          <button class="btn btn--gold" type="submit">Subscribe <i class="arr"></i></button>
        </form>
      </div>
    </section>
'''
    page("news/", "News & Milestones | Guilgal International",
         "News, project milestones and insights from Guilgal International.", "News & Milestones", body, p)


def contact():
    p = "../"
    body = page_hero(p, "guilgal_approach_natural_mirrored.png", "Contact <em>Us</em>",
                     "We welcome enquiries from mining companies, technical partners, investors and strategic collaborators.") + f'''
    <section class="enquiry enquiry--light ivory">
      <div class="wrap enquiry__grid">
        <div>
          <h2>Get in <em>Touch</em></h2>
          <p>Email <a href="mailto:{EMAIL}">{EMAIL}</a> or use the form.</p>
          <p class="small">Guilgal International Ltd, registered in England and Wales.</p>
        </div>
        {enquiry_form(p, with_projects=False)}
      </div>
    </section>
'''
    page("contact/", "Contact | Guilgal International",
         f"Contact Guilgal International at {EMAIL}.", "Contact", body, p)


def members_login():
    p = "../"
    body = page_hero(p, "guilgal_hero_background_1920x1080.png", "Partner <em>Access</em>",
                     "Project pages are private and available to invited partners only.") + f'''
    <section class="enquiry enquiry--light ivory">
      <div class="wrap enquiry__grid">
        <div>
          <h2>Sign <em>in</em></h2>
          <p>Access is by invitation. If you have not received an invitation, please make an investor enquiry.</p>
          <a class="link link--dark" href="{p}investors/#enquiry">Request access <i class="arr"></i></a>
        </div>
        <!-- MEMBERS: replace with the hosting platform's members login (e.g. Wix Members, Netlify Identity) -->
        <form class="form" novalidate data-form>
          <label class="field"><span>Email*</span><input type="email" name="email" autocomplete="username" required></label>
          <label class="field"><span>Password*</span><input type="password" name="password" autocomplete="current-password" required></label>
          {form_status()}
          <button class="btn btn--gold" type="submit">Sign in <i class="arr"></i></button>
        </form>
      </div>
    </section>
'''
    page("members/", "Partner Access | Guilgal International", "Partner sign in.", "Projects", body, p, noindex=True)


def member_project(slug, name, country, mineral, img):
    p = "../../../"
    milestones = [n for n in NEWS if n["project"] == slug]
    ms = ("".join(f'<li><time datetime="{n["date"]}">{e(n["label"])}</time> {e(n["title"])}</li>' for n in milestones)
          or "<li>Milestones will appear here as they are published in News &amp; Milestones.</li>")
    role = ('<p class="role-note">Guilgal International\'s role on this project is commercial facilitation and introductions only.</p>'
            if slug == "hydropower" else "")
    tbs = '<p class="placeholder">[To be supplied]</p>'
    body = page_hero(p, "guilgal_hero_background_1920x1080.png", e(name),
                     f"{e(country)} · {e(mineral)}", "Members only") + f'''
    <section class="dossier ivory">
      <div class="wrap dossier__grid">
        <div class="dossier__main">
          <p class="indicative">Information is indicative and subject to technical review and agreement.</p>
          {role}
          <h2>Project overview</h2>{tbs}
          <h2>Licence and location</h2>{tbs}
          <h2>Geology</h2>{tbs}
          <h2>Work completed</h2>{tbs}
          <h2>Proposed next steps</h2>{tbs}
          <h2>Milestones</h2>
          <ul class="milestones">{ms}</ul>
        </div>
        <aside class="dossier__side">
          <div class="pcard__photo"><img src="{p}public/images/{img}" alt=""></div>
          <a class="btn btn--gold" href="#" aria-disabled="true">Download Project Brief <i class="arr"></i></a>
          <a class="btn btn--outline btn--dark" href="mailto:{EMAIL}?subject={e(name)}">Contact Guilgal International</a>
          <p class="small">Information is indicative and subject to technical review and agreement.</p>
        </aside>
      </div>
    </section>
'''
    page(f"members/projects/{slug}/", f"{name} | Partner Access | Guilgal International",
         "Private project page.", "Projects", body, p, noindex=True)


def legal(slug, title):
    p = "../"
    body = page_hero(p, "guilgal_approach_natural_mirrored.png", e(title)) + f'''
    <section class="split ivory">
      <div class="wrap legal">
        <p class="placeholder">[{e(title)} to be supplied before launch.]</p>
        <p>Guilgal International Ltd, registered in England and Wales. Contact: <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
        <p class="small">{DISCLAIMER}</p>
      </div>
    </section>
'''
    page(f"{slug}/", f"{title} | Guilgal International", f"{title} for Guilgal International.", "", body, p)


def seo_files():
    public = ["", "about/", "about/team/", "projects/", "investors/", "news/", "contact/", "privacy/", "cookies/", "terms/"]
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{SITE_URL}/{u}</loc></url>\n" for u in public) + "</urlset>\n")
    (ROOT / "robots.txt").write_text(
        "User-agent: *\nDisallow: /members/\n\nSitemap: " + SITE_URL + "/sitemap.xml\n")


if __name__ == "__main__":
    home(); about(); team(); projects(); investors(); news(); contact(); members_login()
    for pr in PROJECTS:
        member_project(*pr)
    legal("privacy", "Privacy Policy"); legal("cookies", "Cookie Policy"); legal("terms", "Terms of Use")
    seo_files()
    print("built")
