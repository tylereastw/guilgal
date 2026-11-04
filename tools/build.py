#!/usr/bin/env python3
"""Build the Guilgal International website (design v2, from John Boardman's mock-ups).

    python3 tools/build.py

All copy lives in the data blocks below. Writing rules: British English, no em
dashes (the build refuses to write a page that contains one), always
"Guilgal International", no invented phone numbers, offices, credentials,
figures, tonnages, grades, timelines or ownership splits. Project facts below
are taken from John Boardman's mock-ups and are marked for technical review.
The previous design is kept in archive/editorial-v1/.
"""
from html import escape
from pathlib import Path
import segno

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://www.guilgal.org"
EMAIL = "john@guilgal.org"
IMG = "public/images/v2/"
DISCLAIMER = ("Guilgal International does not provide investment, financial or legal advice. "
              "Nothing on this site is an offer or solicitation.")
INDICATIVE = "Information is indicative and subject to technical review and agreement."


def e(s):
    return escape(s, quote=True)


# ---------------------------------------------------------------- icons (24px line icons)
ICONS = {
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "back": '<path d="M19 12H5M11 6l-6 6 6 6"/>',
    "cubes": '<path d="M3 15l5-3 5 3-5 3zM3 15v4l5 3 5-3v-4M11 9l5-3 5 3-5 3zM11 9v4l5 3 5-3V9M7 6l5-3 5 3"/>',
    "crystal": '<path d="M12 2l-3 6 3 14 3-14zM9 8l-5 4 8 10M15 8l5 4-8 10M6 4l3 4M18 4l-3 4"/>',
    "handshake": '<path d="M2 12l4-4 4 2 3-2 4 1 5 3M6 8v6l5 5c1 1 2 1 3 0l5-5M10 14l2 2M12 12l3 3"/>',
    "search": '<circle cx="11" cy="11" r="6"/><path d="M20 20l-4.5-4.5"/>',
    "gear": '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M5 19l2-2M17 7l2-2"/><circle cx="12" cy="12" r="7"/>',
    "chart": '<path d="M4 20h16M6 16v-3M10 16V9M14 16v-5M18 16V6M6 11l4-4 4 3 5-5"/>',
    "pin": '<path d="M12 22s7-7 7-12a7 7 0 10-14 0c0 5 7 12 7 12z"/><circle cx="12" cy="10" r="2.5"/>',
    "layers": '<path d="M12 3l9 5-9 5-9-5zM3 13l9 5 9-5M3 17l9 5 9-5"/>',
    "pulse": '<path d="M2 12h4l2-6 4 12 3-9 2 3h5"/>',
    "target": '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4"/><path d="M12 2v4M12 18v4M2 12h4M18 12h4"/>',
    "bars": '<path d="M3 20h18M5 20v-4h6v4M13 20v-4h6v4M8 16v-4h8v4"/>',
    "people": '<circle cx="12" cy="7" r="3"/><circle cx="5" cy="10" r="2.3"/><circle cx="19" cy="10" r="2.3"/><path d="M7 20c0-3 2-6 5-6s5 3 5 6M1 19c0-2 2-4 4-4M23 19c0-2-2-4-4-4"/>',
    "doc": '<path d="M6 2h9l5 5v15H6zM15 2v5h5M9 12h8M9 16h8M9 8h3"/>',
    "pick": '<path d="M4 20l10-10M14 4c3 0 6 3 6 6M8 6c4-3 9-2 12 2"/>',
    "atom": '<circle cx="12" cy="12" r="1.5"/><ellipse cx="12" cy="12" rx="10" ry="4"/><ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(60 12 12)"/><ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(120 12 12)"/>',
    "diamond": '<path d="M6 3h12l4 6-10 12L2 9zM2 9h20M9 3l-2 6 5 12 5-12-2-6"/>',
    "leaf": '<path d="M5 19C5 10 11 4 20 4c0 9-6 15-15 15zM5 19l8-8"/>',
    "bolt": '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',
    "tower": '<path d="M8 22l4-20 4 20M9 16h6M10 11h4M4 6h16M6 6l-2 4M18 6l2 4"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2c3 3 4 6 4 10s-1 7-4 10c-3-3-4-6-4-10s1-7 4-10z"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
    "africa": '<path d="M9 2l4 1 3 3 5 1-1 4-3 3 1 4-3 3-2 2-2-3 1-4-4-2-3-4 1-4z"/>',
    "drill": '<path d="M10 22V8l2-6 2 6v14M7 22h10M8 12h8M12 2v20"/>',
    "dam": '<path d="M2 20h20M4 20V8h16v12M8 8v12M12 8v12M16 8v12M2 8h20"/>',
    "map": '<path d="M3 6l6-3 6 3 6-3v15l-6 3-6-3-6 3zM9 3v15M15 6v15"/>',
    "sample": '<path d="M9 3h6M10 3v6l-5 9a2 2 0 002 3h10a2 2 0 002-3l-5-9V3M7 15h10"/>',
    "shield": '<path d="M12 2l8 3v6c0 5-3.5 9-8 11-4.5-2-8-6-8-11V5z"/><path d="M8 12l3 3 5-6"/>',
}


def ico(name, cls="ico"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'


def dot(name, lg=False):
    return f'<span class="ico-dot{" ico-dot--lg" if lg else ""}">{ico(name)}</span>'


# ---------------------------------------------------------------- shared data
NAV = [
    ("Home", ""),
    ("About", "about/", [("About Guilgal International", "about/"), ("Our Name", "about/#our-name"), ("Meet the Team", "about/team/")]),
    ("Projects", "projects/"),
    ("Investors", "investors/"),
    ("News & Milestones", "news/"),
    ("Contact", "contact/"),
]

PROJECTS = [
    # slug, card name, country label, card image
    ("pumba", "Pumba Copper & Gold", "DRC"),
    ("alpha", "Alpha Tantalum & Tin", "DRC"),
    ("nizi-baluma", "Nizi–Baluma Gold", "DRC"),
    ("ndela-mpaza", "Ndela–Mpaza", "DRC"),
    ("hydropower", "Hydropower Projects", "DRC"),
    ("tumfa", "Ghana Tumfa Gold", "Ghana"),
]

APPROACH = [  # John Boardman's wording (About page mock-up)
    ("doc", "Identify", "Source and review promising project opportunities."),
    ("gear", "Evaluate", "Coordinate geological, technical and commercial assessment."),
    ("people", "Partner", "Bring together project owners, specialists and strategic partners."),
    ("chart", "Develop", "Support progress towards structured, responsible and commercially viable outcomes."),
]

NEWS = [  # placeholders until the first posts are published
    dict(kind="news", label="Coming soon", project="", image="about-who.jpg", title="Our first update will be published here shortly"),
    dict(kind="news", label="Coming soon", project="", image="tumfa-hero.jpg", title="Partnership news to follow"),
    dict(kind="news", label="Coming soon", project="", image="home-hero.jpg", title="Milestones will be shared as they are reached"),
    dict(kind="insight", label="Insights", project="", image="about-river.jpg", title="Guides and insights are in preparation"),
]


# ---------------------------------------------------------------- QR codes
def qr(path, name):
    """Real, scannable QR code for SITE/path, saved as SVG; returns the file name."""
    out = ROOT / IMG / "qr" / f"{name}.svg"
    out.parent.mkdir(parents=True, exist_ok=True)
    segno.make(SITE + "/" + path, error="m").save(str(out), scale=6, dark="#10291F", light=None, border=0)
    return f"qr/{name}.svg"


def qr_panel(p, path, name, title, text, button=None, stack=False):
    code = qr(path, name)
    img = f'<img class="qr__code" src="{p}{IMG}{code}" alt="QR code linking to {e(SITE + "/" + path)}" width="112" height="112">'
    if stack:
        return f'<figure class="qr qr--stack">{img}<figcaption class="qr__title">{title}</figcaption></figure>'
    btn = f'<a class="btn btn--gold btn--sm" href="{p}{path}">{e(button)}</a>' if button else ""
    return f'<aside class="qr">{img}<div><p class="qr__title">{title}</p><p>{e(text)}</p>{btn}</div></aside>'


# ---------------------------------------------------------------- page frame
def brand(p):
    return f'''<a class="brand" href="{p}" aria-label="Guilgal International home">
      <img class="brand__emblem" src="{p}{IMG}logo-emblem.jpg" alt="" width="74" height="74">
      <span class="brand__text"><span class="brand__name">GUILGAL</span><span class="brand__intl">INTERNATIONAL</span><span class="brand__tag">EXPLORATION | DEVELOPMENT | PARTNERSHIPS</span></span>
    </a>'''


def header(p, active):
    items = []
    for item in NAV:
        label, href = item[0], item[1]
        cur = ' aria-current="page"' if label == active else ""
        if len(item) == 3:
            sub = "".join(f'<li><a href="{p}{h}">{e(l)}</a></li>' for l, h in item[2])
            items.append(f'<li class="nav__item nav__item--has-sub"><a href="{p}{href}"{cur}>{e(label)}</a>'
                         f'<button class="nav__subtoggle" aria-expanded="false" aria-label="Show About pages"><i></i></button><ul class="nav__sub">{sub}</ul></li>')
        else:
            items.append(f'<li class="nav__item"><a href="{p}{href}"{cur}>{e(label)}</a></li>')
    return f'''<header class="nav" id="top">
    {brand(p)}
    <nav class="nav__links" id="menu" aria-label="Main">
      <ul class="nav__list">{"".join(items)}</ul>
      <a class="btn btn--gold nav__cta" href="{p}investors/#enquiry">Investor Enquiries</a>
    </nav>
    <button class="burger" aria-expanded="false" aria-controls="menu" aria-label="Menu"><span></span><span></span><span></span></button>
  </header>'''


def footer(p):
    links = "".join(f'<a href="{p}{n[1]}">{e(n[0])}</a>' for n in NAV[1:])
    return f'''<footer class="footer">
    <div class="wrap footer__top">
      <div>
        {brand(p)}
        <p class="footer__lines">Mining • Critical Minerals • Project Development • Strategic Partnerships</p>
        <p class="footer__motto">Connecting Opportunities. Developing Partnerships.</p>
      </div>
      <nav class="footer__nav" aria-label="Footer">{links}<a href="mailto:{EMAIL}">{EMAIL}</a></nav>
    </div>
    <div class="wrap footer__bottom">
      <p class="footer__disclaimer">{DISCLAIMER}</p>
      <p>Guilgal International Ltd, registered in England and Wales. <a href="{p}privacy/">Privacy</a> · <a href="{p}cookies/">Cookies</a> · <a href="{p}terms/">Terms</a></p>
    </div>
  </footer>'''


def page(path, title, desc, active, body, p, noindex=False):
    robots = '\n  <meta name="robots" content="noindex, nofollow, noarchive">' if noindex else ""
    canon = "" if noindex else f'\n  <link rel="canonical" href="{SITE}/{path}">'
    html = f'''<!doctype html>
<html lang="en-GB">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(title)}</title>
  <meta name="description" content="{e(desc)}">{robots}{canon}
  <link rel="preload" href="{p}assets/fonts/v2/Montserrat-normal-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="{p}assets/fonts/v2/OpenSans-normal-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="{p}css/fonts.css">
  <link rel="stylesheet" href="{p}css/styles.css">
</head>
<body>
  <a class="skip" href="#main">Skip to main content</a>
  {header(p, active)}
  <main id="main">
{body}
  </main>
  {footer(p)}
  <script src="{p}js/main.js"></script>
</body>
</html>
'''
    assert "—" not in html, f"em dash in {path}"
    out = ROOT / path / "index.html" if path else ROOT / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)


def hero(p, image, inner, cls="hero--page", side=""):
    return f'''    <section class="hero {cls}">
      <div class="hero__bg"><img src="{p}{IMG}{image}" alt=""></div>
      <div class="wrap hero__inner">
        <div class="hero__text">{inner}</div>
        {side}
      </div>
    </section>
'''


def strip(items, n=3):
    lis = "".join(f'<li>{ico(i)}<div><strong>{e(t)}</strong><span>{e(s)}</span></div></li>' for i, t, s in items)
    return f'    <section class="strip"><ul class="strip__list" style="--n:{n}">{lis}</ul></section>\n'


def project_cards(p):
    return '<ul class="pcards">' + "".join(
        f'''<li class="pcard"><a href="{p}members/projects/{s}/" rel="nofollow">
          <div class="pcard__photo"><img src="{p}{IMG}card-{s}.jpg" alt="" loading="lazy"></div>
          <div class="pcard__body"><strong>{e(n)}</strong><span>{e(c)}</span><i class="arrow-circle">{ico("arrow")}</i></div>
          <span class="pcard__access">Partner access</span></a></li>''' for s, n, c in PROJECTS) + "</ul>"


def approach_row():
    return '<ol class="approach">' + "".join(
        f'<li><span class="approach__num">{i}</span>{ico(ic)}<h3>{t}</h3><p>{d}</p></li>'
        for i, (ic, t, d) in enumerate(APPROACH, 1)) + "</ol>"


def news_cards(p, items):
    return '<ul class="ncards" data-feed>' + "".join(
        f'''<li class="ncard" data-kind="{n["kind"]}" data-project="{n["project"]}"><a href="{p}news/">
          <div class="ncard__photo"><img src="{p}{IMG}{n["image"]}" alt="" loading="lazy"></div>
          <div class="ncard__body"><span class="ncard__kind">{e(n["label"])}</span><h3>{e(n["title"])}</h3><i class="arrow-circle">{ico("arrow")}</i></div>
        </a></li>''' for n in items) + "</ul>"


def consent(p):
    return (f'<label class="consent"><input type="checkbox" name="consent" required><span>I agree that Guilgal International may store and process '
            f'these details to respond to my enquiry. See the <a href="{p}privacy/">Privacy Policy</a>.*</span></label>')


def enquiry_form(p, title="Send Us a Message", projects=True):
    opts = "".join(f'<option value="{s}">{e(n)}</option>' for s, n, _ in PROJECTS)
    area = (f'<label class="field"><span>Area of interest*</span><select name="interest" required><option value="">Select a project</option>'
            f'{opts}<option value="general">General partnership enquiry</option></select></label>') if projects else ""
    org = ('<div class="form__row"><label class="field"><span>Organisation</span><input name="organisation" autocomplete="organization"></label>'
           '<label class="field"><span>Country</span><input name="country" autocomplete="country-name"></label></div>') if projects else ""
    return f'''<div class="formcard"><h3 class="formcard__head">{title}</h3>
        <form class="form" novalidate data-form>
          <div class="form__row"><label class="field"><span>Name*</span><input name="name" autocomplete="name" required></label>
          <label class="field"><span>Email*</span><input type="email" name="email" autocomplete="email" required></label></div>
          {org}{area}
          <label class="field"><span>Your enquiry*</span><textarea name="message" rows="4" required></textarea></label>
          {consent(p)}
          <p class="form__msg" role="alert" hidden></p>
          <button class="btn btn--gold" type="submit">Submit enquiry {ico("arrow")}</button>
        </form></div>'''


def contact_block(p):
    return f'''    <section class="section" id="contact-us">
      <div class="wrap contact3">
        <div>
          <div class="shead"><h2>Get in Touch</h2></div>
          <p class="lead">We welcome enquiries from investors, partners and strategic collaborators worldwide.</p>
          <ul class="contact-list"><li>{dot("mail")}<div><strong>Email us</strong><a href="mailto:{EMAIL}">{EMAIL}</a></div></li></ul>
          <p class="small" style="margin-top:18px">Guilgal International Ltd, registered in England and Wales.</p>
        </div>
        {enquiry_form(p)}
        <div class="stay">
          <div>
            <div class="shead"><h2>Stay Informed</h2></div>
            <p class="small">Subscribe for project updates, news and milestones.</p>
            <form class="subscribe" novalidate data-form><label class="sr" for="sub-email">Email address</label>
              <input id="sub-email" type="email" name="email" placeholder="Your email address" required><button class="btn btn--gold" type="submit">Subscribe</button></form>
            <p class="form__msg small" role="alert" hidden></p>
          </div>
          {qr_panel(p, "news/", "news", "Scan for updates", "", stack=True)}
        </div>
      </div>
    </section>
'''


# ---------------------------------------------------------------- pages
def home():
    p = ""
    side = qr_panel(p, "projects/", "projects", "Scan to explore our projects", "", stack=True)
    inner = f'''<p class="hero__eyebrow">Mineral Exploration &amp; Strategic Development</p>
          <h1>Unlocking Africa's<br>Mineral Potential</h1>
          <p class="hero__sub">Connecting high-potential mineral projects with technical expertise, development partners and international partnerships.</p>
          <div class="hero__actions"><a class="btn btn--gold" href="projects/">Explore Our Projects {ico("arrow")}</a><a class="btn btn--line" href="investors/#enquiry">Investor Enquiries {ico("arrow")}</a></div>'''
    body = hero(p, "home-hero.jpg", inner, "hero--home", side) + strip([
        ("cubes", "Copper & Gold", "Exploration opportunities"),
        ("crystal", "Critical Minerals", "Strategic resources"),
        ("handshake", "Strategic Partnerships", "Lasting value")]) + f'''
    <section class="section">
      <div class="wrap grid-2">
        <div>
          <p class="label">Who we are</p>
          <h2>Advancing Africa's Mineral Opportunities</h2>
          <p class="lead">Guilgal International is a project development and strategic facilitation business focused on advancing mineral opportunities in the Democratic Republic of the Congo, Ghana and across Africa.</p>
          <p class="lead">We work alongside local project owners, geological specialists, technical consultants and international partners.</p>
          <a class="btn btn--dark" href="about/">About us {ico("arrow")}</a>
        </div>
        <div class="photo"><img src="{IMG}about-who.jpg" alt="Rocky outcrop above a wide green valley and table mountains" loading="lazy"></div>
      </div>
    </section>

    <section class="section section--cream2">
      <div class="wrap">
        <div class="shead"><h2>Our Projects</h2></div>
        <p class="lead">Six projects across copper and gold, tantalum and tin, critical minerals, gold tailings, Ghana gold and hydropower facilitation. Project details are available to registered partners.</p>
        {project_cards(p)}
        <p style="margin-top:22px"><a class="btn btn--line-dark" href="projects/">Explore Our Projects {ico("arrow")}</a></p>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <p class="label">Our approach</p>
        {approach_row()}
      </div>
    </section>

    <section class="section section--cream2">
      <div class="wrap">
        <div class="shead"><h2>Latest News &amp; Milestones</h2></div>
        {news_cards(p, NEWS[:3])}
      </div>
    </section>

    <section class="band">
      <div class="band__bg"><img src="{IMG}about-hero.jpg" alt=""></div>
      <div class="wrap band__grid">
        <div><p class="label">Partner with us</p><h2>Partner with Guilgal International</h2>
          <p>We welcome enquiries from mining companies, technical partners, investors and strategic collaborators worldwide.</p>
          <div class="hero__actions"><a class="btn btn--gold" href="investors/#enquiry">Investor Enquiries {ico("arrow")}</a><a class="btn btn--line" href="contact/">Contact Guilgal International {ico("arrow")}</a></div></div>
        {qr_panel(p, "investors/", "investors", "Investor Centre", "Scan to visit the Investor Centre.", "Investor Centre")}
      </div>
    </section>
'''
    page("", "Guilgal International | Unlocking Africa's Mineral Potential",
         "Guilgal International connects high-potential mineral projects in the DRC and Ghana with technical expertise and international partners.",
         "Home", body, p)


def about():
    p = "../"
    inner = f'''<p class="label label--light">About Guilgal International</p>
          <h1>People. Projects.<br>Partnerships.</h1>
          <p class="hero__sub">Connecting mineral opportunity with technical expertise, strategic relationships and responsible development across Africa.</p>
          <a class="btn btn--gold" href="{p}projects/">Explore Our Projects {ico("arrow")}</a>'''
    whatwedo = [("search", "Project Identification", "We help identify and assess high-potential mineral opportunities with commercial and geological upside."),
                ("gear", "Technical Coordination", "We support the planning and coordination of geological review, exploration activity and technical work programmes."),
                ("handshake", "Strategic Partnerships", "We connect project owners with investors, mining companies, contractors and commercial partners."),
                ("chart", "Development Support", "We assist in shaping opportunities towards investment readiness, structured negotiations and sustainable development pathways.")]
    minerals = [("copper", "Copper", "Energy transition and industrial growth"), ("gold", "Gold", "Enduring value and development potential"),
                ("tantalum", "Tantalum", "Specialist and strategic applications"), ("tin", "Tin", "Essential industrial mineral"),
                ("critical", "Critical Minerals", "Emerging opportunities in future-facing commodities")]
    body = hero(p, "about-hero.jpg", inner) + f'''
    <section class="section">
      <div class="wrap grid-2">
        <div>
          <p class="label">Who we are</p>
          <h2>Advancing Africa's Mineral Opportunities</h2>
          <p class="lead">Guilgal International is a project development and strategic facilitation business focused on advancing mineral opportunities across Africa.</p>
          <p class="lead">We work alongside local project owners, geological specialists, technical consultants and international partners to help move promising opportunities from concept and early-stage assessment towards technical evaluation, investment readiness and commercial development.</p>
          <p class="lead">Our work is built around practical collaboration, responsible development and long-term value creation.</p>
        </div>
        <div class="photo"><img src="{p}{IMG}about-who.jpg" alt="Rocky outcrop above a wide green valley and table mountains"></div>
      </div>
    </section>

    <section class="section section--cream2" id="what-we-do">
      <div class="wrap">
        <p class="label">What we do</p>
        <ul class="cols4">{"".join(f"<li>{dot(i, True)}<h3>{t}</h3><p>{d}</p></li>" for i, t, d in whatwedo)}</ul>
      </div>
    </section>

    <section class="section section--dark on-dark">
      <div class="wrap">
        <p class="label">Our focus minerals</p>
        <p class="lead">Guilgal International is focused on mineral opportunities aligned with industrial demand, strategic development and long-term global relevance.</p>
        <ul class="minerals">{"".join(f'<li><img src="{p}{IMG}mineral-{s}.jpg" alt="{t} sample" loading="lazy"><strong>{t}</strong><span>{d}</span></li>' for s, t, d in minerals)}</ul>
      </div>
    </section>

    <section class="section">
      <div class="wrap geo">
        <div>
          <p class="label">Our geographic focus</p>
          <h2>Democratic Republic of the Congo and Beyond</h2>
          <p class="lead">Guilgal International's primary focus is on opportunities in the Democratic Republic of the Congo, with broader interest in selected mineral prospects and strategic partnerships elsewhere in Africa.</p>
          <p class="lead">Our approach is grounded in local engagement, international connectivity and a practical understanding of what is required to move opportunities forward.</p>
          <a class="btn btn--gold btn--sm" href="{p}projects/">Our Projects {ico("arrow")}</a>
        </div>
        <img src="{p}{IMG}africa-drc.jpg" alt="Map of Africa with the Democratic Republic of the Congo highlighted" loading="lazy">
        <ul class="places"><li><h4>Selected areas of interest</h4></li>
          <li>{ico("pin")}Democratic Republic of the Congo</li><li>{ico("pin")}Ghana</li><li>{ico("pin")}Other African opportunities</li></ul>
        <div class="photo"><img src="{p}{IMG}about-river.jpg" alt="River winding through forested hills" loading="lazy"></div>
      </div>
    </section>

    <section class="section section--cream2" id="approach">
      <div class="wrap"><p class="label">Our approach</p>{approach_row()}</div>
    </section>

    <section class="section" id="our-name">
      <div class="wrap grid-2">
        <div>
          <p class="label">Our name. Our purpose.</p>
          <h2>Guilgal: A Name Rooted in New Beginnings</h2>
          <p class="lead">The name Guilgal, the French form of the ancient Hebrew name Gilgal, carries an association with renewal, progress and new beginnings.</p>
          <p class="lead">For Guilgal International, these principles reflect our commitment to identifying opportunities, building trusted partnerships and transforming mineral resources and infrastructure potential into sustainable economic development.</p>
          <p class="label" style="margin-top:22px">Rooted in Africa. Connected globally.</p>
        </div>
        <div class="photo"><img src="{p}{IMG}team-hero.jpg" alt="Two engineers in hard hats looking over a river valley" loading="lazy"></div>
      </div>
    </section>

    <section class="band">
      <div class="band__bg"><img src="{p}{IMG}home-hero.jpg" alt=""></div>
      <div class="wrap band__grid">
        <div><p class="label">Why work with Guilgal International?</p><h2>A Trusted Partner for Sustainable Growth</h2>
          <p>Guilgal International offers a practical bridge between mineral opportunity and commercial advancement. We combine project visibility, strategic relationships and development-focused thinking to help unlock value for project owners, partners and investors.</p>
          <div class="hero__actions"><a class="btn btn--gold" href="{p}investors/#enquiry">Investor Enquiries {ico("arrow")}</a><a class="btn btn--line" href="{p}contact/">Contact Guilgal International {ico("arrow")}</a></div></div>
        {qr_panel(p, "projects/", "projects", "Explore Guilgal International's opportunities", "Scan to view our mineral projects and partnership opportunities.", "Scan to explore")}
      </div>
    </section>
'''
    page("about/", "About | Guilgal International",
         "Guilgal International is a project development and strategic facilitation business advancing mineral opportunities in the DRC, Ghana and across Africa.",
         "About", body, p)


TEAM = [
    dict(name="John Boardman", role="Director, Guilgal International",
         sub="Former CEO, 1620 Capital | International Mining Investment & Corporate Development", photo="team-john.jpg",
         bio=["John Boardman is responsible for Guilgal International's corporate strategy, international partnerships, investor relations and commercial project development.",
              "He has extensive experience in the mining sector, including his previous role as Chief Executive Officer of 1620 Capital in Perth, Western Australia, where he was involved in identifying, structuring and advancing mineral resource opportunities with ASX- and AIM-listed companies.",
              "John focuses on connecting African mineral opportunities with international partners, technical expertise and development capital."],
         keys=[("handshake", "Strategic partnerships"), ("people", "Investor engagement"), ("chart", "Corporate development"), ("target", "Project origination and transaction support")]),
    dict(name="Gedeon Ngoy Makonga Pelesa", role="Title to be confirmed", sub="Geological coordination | Project development", photo=None,
         bio=["Gedeon Ngoy Makonga Pelesa supports Guilgal International's project activities in the Democratic Republic of the Congo, contributing extensive local knowledge, project coordination and geological engagement across key mineral opportunities.",
              "Gedeon plays a key role in advancing Guilgal International's mineral projects, including copper, gold, tantalum, tin and critical minerals, and coordinates field activities, technical studies and local partnerships."],
         keys=[("pick", "Geological coordination"), ("map", "Project identification and evaluation"), ("people", "Local partnerships and stakeholder engagement"), ("leaf", "Field activities and technical support")]),
    dict(name="Didier", role="Title to be confirmed", sub="Business development | Strategic relationships", photo=None,
         bio=["Didier contributes to Guilgal International's in-country relationships, commercial coordination and project development support in the Democratic Republic of the Congo.",
              "He plays an important role in business development, government and stakeholder engagement, and the facilitation of strategic partnerships across Guilgal International's project portfolio."],
         keys=[("handshake", "Business development"), ("people", "Government and stakeholder engagement"), ("chart", "Strategic partnerships"), ("gear", "Project coordination and commercial support")]),
]


def team():
    p = "../../"
    inner = '''<p class="label label--light">Our people</p><h1>Meet the Team</h1>
          <p class="hero__sub">The people behind Guilgal International's project origination, partnerships and development activities across Africa.</p>'''
    cards = []
    for t in TEAM:
        photo = f'<img src="{p}{IMG}{t["photo"]}" alt="Portrait of {e(t["name"])}">' if t["photo"] else f'<b aria-hidden="true">{e(t["name"][0])}</b>'
        keys = "".join(f"<li>{ico(i)}{e(k)}</li>" for i, k in t["keys"])
        cards.append(f'''<li class="person">
          <div class="person__photo">{photo}</div>
          <div class="person__head"><h2>{e(t["name"])}</h2><p class="person__role">{e(t["role"])}</p><p class="person__sub">{e(t["sub"])}</p></div>
          <div class="person__body">{"".join(f"<p>{e(b)}</p>" for b in t["bio"])}<h3>Key areas</h3><ul class="keys">{keys}</ul></div>
        </li>''')
    body = hero(p, "team-hero.jpg", inner) + strip([
        ("globe", "International experience", ""), ("africa", "Local knowledge", ""), ("handshake", "Strategic partnerships", ""),
        ("chart", "Project development", ""), ("leaf", "Responsible growth", "")], 5) + f'''
    <section class="section"><div class="wrap"><ul class="people">{"".join(cards)}</ul>
      <p class="small" style="margin-top:16px">Portraits of Gedeon and Didier, and their titles, will be added once supplied and approved.</p></div></section>

    <section class="band">
      <div class="band__bg"><img src="{p}{IMG}about-river.jpg" alt=""></div>
      <div class="wrap band__grid"><blockquote class="band__quote">"International connections, local expertise and shared commitment to responsible development."</blockquote></div>
    </section>
'''
    page("about/team/", "Meet the Team | Guilgal International", "The people behind Guilgal International.", "About", body, p)


def projects():
    p = "../"
    inner = f'''<p class="label label--light">Our projects</p><h1>A Portfolio Across<br>the DRC and Ghana</h1>
          <p class="hero__sub">Guilgal International works on six projects in the Democratic Republic of the Congo and Ghana, from early-stage exploration to the reprocessing of historical gold tailings. Full project information, maps, technical summaries and milestones are available to registered partners.</p>
          <div class="hero__actions"><a class="btn btn--gold" href="{p}members/">Partner login {ico("arrow")}</a><a class="btn btn--line" href="{p}investors/#enquiry">Request access {ico("arrow")}</a></div>'''
    body = hero(p, "home-hero.jpg", inner) + f'''
    <section class="section">
      <div class="wrap">
        <div class="shead"><h2>Our Portfolio at a Glance</h2></div>
        {project_cards(p)}
      </div>
    </section>

    <section class="section section--cream2">
      <div class="wrap grid-2">
        <div>
          <p class="label">How partner access works</p>
          <ol class="steps">
            <li><b>1</b><strong>Make an enquiry</strong><span>Tell us about your organisation and the projects you are interested in.</span></li>
            <li><b>2</b><strong>Confidentiality agreement</strong><span>We send a confidentiality agreement for signature.</span></li>
            <li><b>3</b><strong>Approval</strong><span>Once signed and approved, we send your login details.</span></li>
            <li><b>4</b><strong>Project pages</strong><span>Signed-in partners can view project pages, briefs and milestones.</span></li>
          </ol>
        </div>
        <div>
          <p class="label">Our role</p>
          <p class="lead">Guilgal International originates and facilitates projects and brings in partners. On the hydropower and infrastructure projects, our role is limited to commercial facilitation and introductions; we are not the financier, engineer, builder or operator.</p>
          <div class="hero__actions"><a class="btn btn--gold" href="{p}investors/#enquiry">Request access {ico("arrow")}</a><a class="btn btn--line-dark" href="{p}contact/">Contact Guilgal International</a></div>
        </div>
      </div>
    </section>
'''
    page("projects/", "Our Projects | Guilgal International",
         "Guilgal International's portfolio: copper and gold, tantalum and tin, critical minerals, gold tailings, Ghana gold and hydropower facilitation.",
         "Projects", body, p)


def investors():
    p = "../"
    inner = f'''<a class="back" href="{p}projects/">{ico("back")} Back to projects</a>
          <h1>Investor Centre &amp; Contact</h1>
          <p class="hero__meta">Partner with Guilgal International: Unlock the Value of Africa</p>
          <p class="hero__sub">Find out about our project portfolio, request access to project information and get in touch with our team.</p>
          <ul class="pills"><li><a class="pill" href="#portfolio">Project summaries</a></li><li><a class="pill" href="#why">How we partner</a></li><li><a class="pill" href="{p}news/">News &amp; updates</a></li><li><a class="pill" href="#enquiry">Contact us</a></li></ul>'''
    why = [("diamond", "Vetted Opportunities", "Projects are reviewed before they are introduced to partners."),
           ("handshake", "Local Relationships", "Established working relationships with project owners and stakeholders."),
           ("people", "Technical Networks", "Access to geological, technical and commercial specialists."),
           ("leaf", "Responsible Development", "A focus on responsible, structured project progression."),
           ("chart", "Long-Term Partnerships", "Durable relationships rather than single transactions.")]
    body = hero(p, "investors-hero.jpg", inner) + f'''
    <section class="section" id="portfolio">
      <div class="wrap grid-2 why-wrap" style="grid-template-columns:1.55fr 1fr;align-items:start">
        <div><div class="shead"><h2>Our Projects at a Glance</h2></div>{project_cards(p)}</div>
        <div id="why"><div class="shead"><h2>Why Partner with Guilgal International?</h2></div>
          <div class="why-grid">
            <ul class="why">{"".join(f"<li>{dot(i)}<div><strong>{t}</strong><span>{d}</span></div></li>" for i, t, d in why)}</ul>
            <div class="quote-panel"><img src="{p}{IMG}africa-gold.jpg" alt=""><blockquote>"Together we can unlock Africa's mineral and energy potential."</blockquote></div>
          </div>
        </div>
      </div>
    </section>
''' + contact_block(p).replace('id="contact-us"', 'id="enquiry"') + f'''
    <section class="band">
      <div class="band__bg"><img src="{p}{IMG}about-hero.jpg" alt=""></div>
      <div class="wrap band__grid">
        <div><h2 class="band__quote">Building a Sustainable Future with Guilgal International</h2>
          <p>Next steps: explore our projects, discuss partnering with us and join us as we grow in Africa.</p></div>
        <a class="btn btn--gold" href="#enquiry">Contact us today {ico("arrow")}</a>
      </div>
    </section>
'''
    page("investors/", "Investor Centre | Guilgal International",
         "Request access to Guilgal International's project information, get project updates and contact our team about partnering on projects in Africa.",
         "Investors", body, p)


def news():
    p = "../"
    inner = '''<p class="label label--light">News &amp; milestones</p><h1>News &amp; Project Milestones</h1>
          <p class="hero__sub">Dated company news, project milestones and insights from Guilgal International.</p>'''
    opts = "".join(f'<option value="{s}">{e(n)}</option>' for s, n, _ in PROJECTS)
    body = hero(p, "about-river.jpg", inner) + f'''
    <section class="section">
      <div class="wrap">
        <div class="filters" role="group" aria-label="Filter updates">
          <div class="chips"><button type="button" class="chip is-on" data-kind="all" aria-pressed="true">All</button><button type="button" class="chip" data-kind="news" aria-pressed="false">News</button><button type="button" class="chip" data-kind="insight" aria-pressed="false">Insights</button></div>
          <label>Project <select data-project-filter><option value="">All projects</option>{opts}</select></label>
        </div>
        {news_cards(p, NEWS)}
        <p class="feed__empty" hidden>No updates for this selection yet.</p>
      </div>
    </section>
''' + contact_block(p)
    page("news/", "News & Milestones | Guilgal International",
         "Company news and milestones from Guilgal International: partnerships, events and updates on mineral project development in the DRC and Ghana.",
         "News & Milestones", body, p)


def contact():
    p = "../"
    inner = '''<p class="label label--light">Contact</p><h1>Contact Guilgal International</h1>
          <p class="hero__sub">We welcome enquiries from investors, partners and strategic collaborators worldwide.</p>'''
    body = hero(p, "about-hero.jpg", inner) + contact_block(p)
    page("contact/", "Contact | Guilgal International", f"Contact Guilgal International by email at {EMAIL}.", "Contact", body, p)


def members():
    p = "../"
    inner = '''<p class="label label--light">Partner access</p><h1>Partner Login</h1>
          <p class="hero__sub">Project pages are private and available to invited partners only.</p>'''
    body = hero(p, "home-hero.jpg", inner) + f'''
    <section class="section"><div class="wrap grid-2" style="align-items:start">
      <div><h2>Sign in</h2><p class="lead">Access is by invitation. If you have not received an invitation, please make an investor enquiry.</p>
        <a class="btn btn--line-dark" href="{p}investors/#enquiry">Request access {ico("arrow")}</a></div>
      <!-- MEMBERS: replace with the hosting platform's members login before launch -->
      <div class="formcard"><h3 class="formcard__head">Partner login</h3><form class="form" novalidate data-form>
        <label class="field"><span>Email*</span><input type="email" name="email" autocomplete="username" required></label>
        <label class="field"><span>Password*</span><input type="password" name="password" autocomplete="current-password" required></label>
        <p class="form__msg" role="alert" hidden></p><button class="btn btn--gold" type="submit">Sign in {ico("arrow")}</button></form></div>
    </div></section>
'''
    page("members/", "Partner Login | Guilgal International", "Partner sign in.", "Projects", body, p, noindex=True)


# ---------------------------------------------------------------- project pages (members only)
# Copy and figures below come from John Boardman's project mock-ups. They are
# draft, unverified and require competent technical review before release.
PDATA = {
 "pumba": dict(
    title="Pumba Copper & Gold", meta=["PR15201", "Haut-Katanga Province, DRC"],
    lead="A copper and gold exploration project within the mineral-rich Kundelungu formation, with strong IP anomalies and multiple drill targets.",
    pills=["Copper", "Gold", "Sulphides", "Oxides", "Strong IP anomalies"],
    overview=["Pumba (PR15201) is a copper and gold project located in the Haut-Katanga Province of the Democratic Republic of the Congo, within the Kundelungu formation.",
              "Historic work and recent exploration indicate strong IP anomalies with targets from surface to depth. The project offers potential for oxide, mixed and sulphide mineralisation with both copper and gold upside.",
              "Guilgal International is working with local partners to advance exploration, including detailed geophysical interpretation, target generation and a phased drilling programme."],
    highlights=[("pin", "Exploration licence PR15201 secured"), ("layers", "Located in the mineral-rich Kundelungu formation"), ("pulse", "Strong IP geophysical anomalies"),
                ("target", "Multiple priority drill targets (BW01 to BW10)"), ("bars", "Copper and gold potential (oxide to sulphide)"), ("people", "Access to experienced drilling team and regional support")],
    figures=[("Regional geology", "geology", "Outcropping Kundelungu sediments within the project area",
              ["Located within the Kundelungu formation, a major Central African Copperbelt analogue.", "Favourable stratigraphy for sediment-hosted copper with gold potential.",
               "Evidence of oxide, mixed and sulphide mineralisation.", "Regional setting with multiple high-priority targets."]),
             ("IP geophysics: chargeability", "ip", "IP chargeability image showing key target zones (BW01 to BW10)", [])],
    table=("Proposed drill targets (Gedeon)", ["Target", "Depth range (m)", "Comment"],
           [["BW01", "0 to 200", "Priority target"], ["BW02", "70 to 200", "Strong anomaly"], ["BW03", "100 to 200", "Key target"], ["BW04", "100 to 150", "Shallow target"],
            ["BW05", "70 to 200", "Strong anomaly"], ["BW06", "100 to 150", "Key target"], ["BW07", "90 to 100", "Shallow target"], ["BW09", "90 to 200", "Priority target"], ["BW10", "90 to 200", "Priority target"]],
           "Drilling to test IP anomalies and define copper and gold mineralisation from surface to depth."),
    gallery=[("g1", "Outcropping Kundelungu sediments (example)"), ("g2", "Visible copper mineralisation (example)"), ("g3", "Rock chip sample with copper and gold mineralisation (example)"), ("g4", "Exploration drilling in the DRC (regional example)")],
    programme=[("Site visit and detailed geological review", "Confirm targets and refine drill programme."), ("Complete geophysical interpretation", "Integrate IP data and generate drill targets."),
               ("Phase 1 drilling programme", "Test priority targets (BW01 to BW10)."), ("Ongoing exploration and evaluation", "Follow-up drilling and broader project assessment.")],
    timeline=[("Q4 2026", "Site visit and target review"), ("Q1 2027", "Commence drilling"), ("Q2 2027", "Assays and initial results"), ("Q3 to Q4 2027", "Follow-up drilling"), ("2028+", "Resource definition")],
    opportunity="Pumba is a copper and gold exploration project in a proven mineral province. We welcome discussions with investors, joint-venture partners and mining companies to advance exploration and development."),
 "alpha": dict(
    title="Alpha Tantalum & Tin", meta=["PR16516 & PR16517", "Democratic Republic of the Congo"],
    lead="A tantalum and tin project with strong surface indicators, artisanal activity and potential for associated critical minerals.",
    pills=["Tantalum", "Tin", "Critical minerals", "Artisanal activity", "Growth potential"],
    facts=[("pick", "Tantalum & tin", "High-grade surface samples"), ("pin", "PR16516 & PR16517", "Democratic Republic of the Congo"), ("layers", "Artisanal activity", "Historical and current small-scale mining"),
           ("leaf", "Critical minerals", "Potential for REE association"), ("chart", "Development pathway", "Exploration, pilot plant and scale-up potential")],
    overview=["Alpha Tantalum comprises two exploration licences (PR16516 and PR16517) in the Democratic Republic of the Congo, prospective for tantalum (tantalite) and tin (cassiterite), with encouraging surface samples and artisanal activity.",
              "The project also has potential for associated critical minerals, including rare earth elements.",
              "Guilgal International, through Alpha Tantalum SARL, is advancing technical studies, exploration and development options in partnership with local stakeholders."],
    highlights=[("doc", "Two exploration licences (PR16516 & PR16517)"), ("map", "Tantalum and tin mineralisation with strong surface samples"), ("people", "Artisanal mining activity"),
                ("atom", "Potential for associated critical minerals (REE, Rb)"), ("gear", "Pathway from exploration to pilot processing and scale-up"), ("handshake", "Support from local partners and financial institutions")],
    figures=[("Geological setting", "geology", "", ["Located within a prospective tin-tantalum belt.", "Pegmatites and associated granitic intrusions.", "Evidence of tantalum, tin and associated critical minerals.", "Accessible by existing regional infrastructure."]),
             ("Artisanal activity", "artisanal", "", ["Active artisanal mining for tantalite and cassiterite.", "Confirms mineralisation at surface.", "Provides valuable local knowledge and target indicators.", "Supports early-stage bulk sampling and pilot processing."])],
    gallery=[("g1", "Tantalite (tantalum)"), ("g2", "Cassiterite (tin)"), ("plant", "Pilot processing concept (illustrative)")],
    programme=[("Complete detailed geological mapping and sampling", ""), ("Geophysical surveys to refine targets", ""), ("Drilling programme to test key targets", ""),
               ("Preliminary mineral inventory and scoping study", ""), ("Pilot processing and metallurgical test work", ""), ("Development study and financing options", "")],
    opportunity="Alpha offers exposure to tantalum, tin and potential rare earth elements, with a pathway to pilot processing and scale-up. We welcome strategic partners and funding institutions."),
 "ndela-mpaza": dict(
    title="Ndela–Mpaza", meta=["PR15621 & PR15648", "Kweneng, DRC"],
    lead="Prospective for rare earth elements, critical minerals and pegmatites with strong radiometric signatures.",
    pills=["Rare earth elements", "Lithium", "Critical minerals", "Pegmatites"],
    facts=[("diamond", "Rare earth elements", "Strong K, U, Th radiometric signatures"), ("layers", "PR15621 & PR15648", "Kweneng, DRC"), ("crystal", "Pegmatites", "Highly prospective granitic terrains"),
           ("chart", "Critical minerals", "Lithium, REEs and associated elements"), ("target", "Target generation", "Radiometrics, mapping and drilling programme")],
    overview=["Ndela and Mpaza (PR15621 and PR15648) are located in the Kweneng region of the Democratic Republic of the Congo, within prospective granitic terrains known to host pegmatites and critical minerals.",
              "Radiometric surveys indicate strong signatures for potassium (K), uranium (U) and thorium (Th), which can be associated with rare earth elements (REEs), lithium and other critical minerals.",
              "Guilgal International is working with local partners to advance exploration, including detailed mapping, radiometric surveys, target generation and a phased drilling programme."],
    highlights=[("doc", "Two exploration licences (PR15621 & PR15648)"), ("pick", "Strong radiometric signatures (K, U, Th)"), ("crystal", "Pegmatite targets with REE and lithium potential"),
                ("gear", "Systematic target generation and drill testing"), ("handshake", "Support from experienced local partners and regional exploration teams")],
    figures=[("Regional geology", "geology", "", ["Located within the Kweneng granitic complex.", "Pegmatites and associated rare earth element mineralisation.", "Favourable structural setting for critical minerals.", "Accessible by existing regional infrastructure."]),
             ("Radiometric survey (example)", "radiometric", "Radiometric image showing elevated K, U, Th signatures (illustrative example)", []),
             ("Target generation", "targets", "", ["Radiometric interpretation to identify priority zones.", "Detailed geological mapping and sampling.", "Multiple pegmatite targets defined."])],
    gallery=[("g1", "Pegmatite (example)"), ("g2", "Rare earth elements"), ("g3", "Lithium minerals")],
    programme=[("Site visit and detailed mapping", "Confirm access, geology and targets."), ("Geophysical surveys", "Radiometrics and interpretation."), ("Target generation", "Define priority drill targets."),
               ("Diamond drilling programme", "Test key targets."), ("Evaluation and development", "Follow-up drilling and project assessment.")],
    note="The country and province for Ndela–Mpaza are to be confirmed before this page is finalised.",
    opportunity="Ndela–Mpaza is an early-stage project with exposure to high-demand critical minerals. We welcome strategic partners and investors."),
 "nizi-baluma": dict(
    title="Nizi–Baluma Gold", meta=["PE5110", "Ituri Province, DRC"], sub="Tailings Reprocessing & Wider Project",
    lead="A gold opportunity through reprocessing of historical tailings, with longer-term potential in the wider Nizi–Mont Baluma project.",
    pills=["Tailings", "Gold", "CIP processing", "Environmental value", "Long-term potential"],
    facts=[("bars", "Tailings", "Historical tailings (Phase 1B)"), ("target", "Processing", "CIP plant concept"), ("leaf", "Environmental benefit", "Responsible reprocessing and site rehabilitation"),
           ("handshake", "Strategic partnership", "Proposed, subject to agreement"), ("pin", "Ituri Province", "Democratic Republic of the Congo")],
    overview=["The Nizi–Baluma project offers an opportunity to reprocess historical gold tailings, with additional longer-term potential in the wider Nizi–Mont Baluma project area.",
              "Historical studies of the tailings, held under a separate PER, report approximately 1.31 million tonnes (Phase 1B) at an average grade of 1.87 g/t Au. These are historical, unverified estimates.",
              "A 500 t/day CIP processing plant is proposed. The project provides an opportunity for environmental improvement and future development of the underlying mineralised ground (via BALUMA SA, PE5110)."],
    highlights=[("bars", "Historical tailings, approximately 1.31 Mt (Phase 1B, historical estimate)"), ("target", "Average grade 1.87 g/t Au (historical, unverified)"), ("gear", "500 t/day CIP processing plant proposed"),
                ("handshake", "Ownership arrangements proposed, subject to agreement"), ("leaf", "Environmental benefits through rehabilitation and responsible reprocessing")],
    figures=[("Tailings site (example)", "tailings", "", ["Historical gold tailings from previous operations.", "Potential for reprocessing using CIP."]),
             ("Proposed processing plant (500 t/day)", "plant", "", ["CIP plant concept (mid-tier design).", "Metallurgical test work to confirm recovery."]),
             ("Wider project potential", "wider", "", ["Nizi–Mont Baluma project (BALUMA SA, PE5110).", "Opportunity for further exploration and development."])],
    programme=[("Finalise agreements", ""), ("Feasibility studies", ""), ("Permitting and financing", ""), ("Plant construction and mobilisation", ""), ("Commissioning and ramp-up", "")],
    note="Tonnage and grade are historical, unverified estimates. Economics and commercial terms are shared only after a confidentiality agreement and remain subject to agreement.",
    opportunity="Nizi–Baluma combines tailings reprocessing with longer-term exploration upside. We welcome discussions with strategic partners."),
 "tumfa": dict(
    title="Ghana Tumfa Gold", meta=["Kibi Belt", "Eastern Region, Ghana"],
    lead="A gold project with both alluvial and hard-rock potential in Ghana's Kibi greenstone belt.",
    pills=["Gold", "Alluvial & hard-rock", "Established mining region", "Near-term opportunities"],
    facts=[("bars", "Gold potential", "Alluvial and hard-rock gold mineralisation"), ("pin", "Strategic location", "Kibi greenstone belt, Eastern Region, Ghana"), ("handshake", "Established region", "Proven gold endowment and mining activity"),
           ("people", "Local engagement", "Working with project owners and stakeholders"), ("chart", "Development potential", "Exploration and resource definition opportunities")],
    overview=["The Tumfa Gold Project is located in the Kibi greenstone belt in the Eastern Region of Ghana, covering an area of approximately 44.8 to 44.99 km².",
              "The project has both alluvial and hard-rock gold potential, with historical and artisanal mining activity in the area. The Kibi belt is a well-known gold-producing region.",
              "Guilgal International is providing strategic consulting support to the project owners, including technical review, exploration planning and introductions to potential partners and investors."],
    highlights=[("doc", "44.8 to 44.99 km² project area"), ("map", "Both alluvial and hard-rock gold potential"), ("pick", "Located in the prospective Kibi greenstone belt"),
                ("bars", "Historical and artisanal mining activity"), ("gear", "Exploration and resource definition opportunities"), ("handshake", "Guilgal International providing strategic consulting and partner introductions")],
    figures=[("Regional geology", "geology", "", ["Located within the Kibi greenstone belt.", "Favourable geology for gold mineralisation.", "Good access and regional infrastructure."]),
             ("Exploration potential", "exploration", "", ["Alluvial gold targets in river systems and palaeo-channels.", "Hard-rock targets in greenstone sequences and shear zones."]),
             ("Artisanal mining activity", "artisanal", "", ["Historical and current small-scale mining activity.", "Provides valuable local knowledge and target indicators."])],
    programme=[("Detailed review and planning", ""), ("Exploration programme", ""), ("Drilling and target definition", ""), ("Resource estimate", ""), ("Development options and partner funding", "")],
    note="Guilgal International's role on Tumfa is strategic consulting to the project owners.",
    opportunity="Tumfa offers exposure to gold in an established and proven mining region. We welcome discussions with experienced operators and partners."),
 "hydropower": dict(
    title="Hydropower Projects", meta=["Kilubi and Haut-Katanga Dams"], sub="Sustainable energy for the Democratic Republic of the Congo",
    lead="Supporting the development of clean, reliable and affordable hydroelectric power through strategic facilitation and partnerships.",
    pills=["Clean energy", "Infrastructure", "Regional development", "Industrial growth"],
    facts=[("bolt", "Renewable energy", "Clean and reliable power generation"), ("chart", "Economic growth", "Supports industrial development and jobs"), ("tower", "Strategic infrastructure", "Strengthens regional energy supply"),
           ("handshake", "Government support", "Ministry of Energy and Hydropower engagement"), ("people", "Partnership opportunities", "Open to international infrastructure partners")],
    overview=["Guilgal International is working with SHE-QMS as a strategic facilitator for the development of hydroelectric dam projects in the Democratic Republic of the Congo, including the Kilubi project in Haut-Lomami Province and three additional dams in Haut-Katanga Province.",
              "These projects aim to deliver clean, renewable energy to support economic growth, industrial development and improved living standards in the region.",
              "Guilgal International's role is limited to commercial facilitation, introductions and partnership development. We are not providing finance, construction, engineering or operation services."],
    highlights=[("bolt", "Four hydropower projects (1 in Haut-Lomami, 3 in Haut-Katanga)"), ("shield", "Government engagement with the Ministry of Energy and Hydropower"), ("gear", "SHE-QMS leading technical and financing discussions"),
                ("handshake", "Guilgal International role: commercial facilitation and introductions"), ("chart", "Opportunity for regional power supply, mining and industrial growth")],
    figures=[("Kilubi hydropower project", "kilubi", "Haut-Lomami Province", ["Located in Haut-Lomami Province.", "Supports local communities and regional economic development."]),
             ("Haut-Katanga hydropower projects", "katanga", "Three dams, Haut-Katanga Province", ["Three hydropower projects in Haut-Katanga.", "Early-stage development and feasibility discussions."])],
    programme=[("Government engagement", "In progress."), ("Feasibility studies", "Planned."), ("Financing discussions", "Planned, led by SHE-QMS."), ("Approvals and permits", "Planned."), ("Construction and development", "Subject to funding.")],
    role=True,
    opportunity="We welcome discussions with infrastructure investors, development partners and energy offtakers interested in the Kilubi and Haut-Katanga projects."),
}


def project_page(slug, card_name):
    d = PDATA[slug]
    p = "../../../"
    path = f"members/projects/{slug}/"
    meta = ' <span>|</span> '.join(e(m) for m in d["meta"])
    sub = f'<p class="hero__meta">{e(d["sub"])}</p>' if d.get("sub") else ""
    inner = f'''<a class="back" href="{p}projects/">{ico("back")} Back to projects</a>
          <h1>{e(d["title"])}</h1>{sub}
          <p class="hero__meta">{meta}</p>
          <p class="hero__lead">{e(d["lead"])}</p>
          <ul class="pills">{"".join(f'<li><span class="pill">{e(x)}</span></li>' for x in d["pills"])}</ul>
          <div class="hero__actions"><a class="btn btn--gold" href="#" aria-disabled="true">{ico("doc")} Download project brief</a><a class="btn btn--line" href="mailto:{EMAIL}?subject={e(card_name)}">Contact us {ico("arrow")}</a></div>'''
    side = qr_panel(p, path, f"project-{slug}", f"Scan for {e(card_name)} updates", "View project information, technical summaries and latest milestones.")
    body = hero(p, f"{slug}-hero.jpg", inner, "hero--page", side)
    if d.get("facts"):
        body += '    <section class="factbar"><ul class="factbar__list">' + "".join(
            f"<li>{dot(i)}<div><strong>{e(t)}</strong><span>{e(s)}</span></div></li>" for i, t, s in d["facts"]) + "</ul></section>\n"
    role = '<p class="role-note">Guilgal International\'s role on this project is commercial facilitation and introductions only.</p>' if d.get("role") else ""
    note = f'<p class="draft">{e(d["note"])}</p>' if d.get("note") else ""
    body += f'''
    <section class="section section--tight">
      <div class="wrap">
        <p class="draft"><strong>Members only. Draft content from the design mock-up.</strong> {INDICATIVE} Facts and figures require competent technical review before release.</p>
        {role}{note}
        <div class="dgrid">
          <div><p class="label">Project overview</p>{"".join(f"<p>{e(x)}</p>" for x in d["overview"])}</div>
          <div><p class="label">Key highlights</p><ul class="hlist">{"".join(f"<li>{dot(i)}{e(t)}</li>" for i, t in d["highlights"])}</ul></div>
          <figure class="mapcard"><p class="label">Project location</p><img src="{p}{IMG}{slug}-location.jpg" alt="Project location map (illustrative)"></figure>
        </div>
      </div>
    </section>
'''
    figs = []
    for title, img, cap, bullets in d["figures"]:
        bl = "<ul class='bullets'>" + "".join(f"<li>{e(b)}</li>" for b in bullets) + "</ul>" if bullets else ""
        figs.append(f'<div><p class="label">{e(title)}</p><figure><img class="photo" src="{p}{IMG}{slug}-{img}.jpg" alt="{e(cap or title)}" loading="lazy">'
                    f'{f"<figcaption>{e(cap)}</figcaption>" if cap else ""}</figure>{bl}</div>')
    if d.get("table"):
        tt, head, rows, tnote = d["table"]
        figs.append(f'''<div><p class="label">{e(tt)}</p><table class="dtable"><thead><tr>{"".join(f"<th>{h}</th>" for h in head)}</tr></thead>
          <tbody>{"".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)}</tbody></table>
          <div class="note">{ico("drill")}<span>{e(tnote)}</span></div>
          <figure style="margin-top:12px"><img src="{p}{IMG}{slug}-section.jpg" alt="Conceptual section (not to scale)" loading="lazy"><figcaption>Conceptual section (not to scale)</figcaption></figure></div>''')
    cols = "grid-3" if len(figs) >= 3 else "grid-2"
    body += f'    <section class="section section--tight section--cream2"><div class="wrap {cols}" style="align-items:start">{"".join(figs)}</div></section>\n'
    gal = d.get("gallery", [])
    if gal:
        body += ('    <section class="section section--tight"><div class="wrap"><div class="gallery" style="grid-template-columns:repeat(' + str(len(gal)) + ',1fr)">' +
                 "".join(f'<figure><img src="{p}{IMG}{slug}-{g}.jpg" alt="{e(c)}" loading="lazy"><figcaption>{e(c)}</figcaption></figure>' for g, c in gal) + "</div></div></section>\n")
    prog = "".join(f'<li><b>{i}</b><strong>{e(t)}</strong><span>{e(s)}</span></li>' for i, (t, s) in enumerate(d["programme"], 1))
    tl = ""
    if d.get("timeline"):
        tl = (f'<div><p class="label">Indicative timeline</p><ol class="timeline" style="--n:{len(d["timeline"])}">' +
              "".join(f"<li><strong>{e(a)}</strong>{e(b)}</li>" for a, b in d["timeline"]) +
              '</ol><p class="disclaim">Timeline is indicative and subject to funding, access, seasonal conditions and regulatory approvals.</p></div>')
    else:
        tl = '<div><p class="label">Indicative timeline</p><p class="disclaim">An indicative timeline will be added once it has been reviewed and approved.</p></div>'
    body += f'''    <section class="section section--tight">
      <div class="wrap grid-3" style="align-items:start">
        <div><p class="label">{"Development pathway" if slug == "alpha" else "Project status" if slug == "hydropower" else "Next steps" if slug == "nizi-baluma" else "Exploration programme"}</p><ol class="steps">{prog}</ol></div>
        {tl}
        <div class="opp"><p class="label">Partnership opportunity</p><div class="opp__text">{dot("handshake", True)}<p class="small">{e(d["opportunity"])}</p></div>
          <a class="btn btn--gold" href="{p}investors/#enquiry">Investor enquiries {ico("arrow")}</a>
          <a class="btn btn--dark" href="#" aria-disabled="true">Download project brief {ico("arrow")}</a>
          <p class="small">{INDICATIVE}</p></div>
      </div>
    </section>
'''
    rel = "".join(f'<li><a href="{p}members/projects/{s}/"><img src="{p}{IMG}card-{s}.jpg" alt=""><div><strong>{e(n)}</strong><span>{e(c)}</span></div></a></li>'
                  for s, n, c in PROJECTS if s != slug)
    body += f'''    <section class="related"><div class="wrap"><p class="label">Related projects</p><ul class="related__list">{rel}</ul>
      <a class="related__more" href="{p}projects/">View all projects →</a></div></section>
'''
    page(path, f"{d['title']} | Partner Access | Guilgal International", "Private project page.", "Projects", body, p, noindex=True)


def legal(slug, title):
    p = "../"
    body = hero(p, "about-river.jpg", f'<h1>{e(title)}</h1>') + f'''
    <section class="section"><div class="wrap" style="max-width:860px">
      <p class="placeholder">[{e(title)} to be supplied before launch.]</p>
      <p>Guilgal International Ltd, registered in England and Wales. Contact: <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
      <p class="small">{DISCLAIMER}</p></div></section>
'''
    page(f"{slug}/", f"{title} | Guilgal International", f"{title} for Guilgal International.", "", body, p)


def seo():
    pub = ["", "about/", "about/team/", "projects/", "investors/", "news/", "contact/", "privacy/", "cookies/", "terms/"]
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
                                      "".join(f"  <url><loc>{SITE}/{u}</loc></url>\n" for u in pub) + "</urlset>\n")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nDisallow: /members/\nDisallow: /archive/\n\nSitemap: {SITE}/sitemap.xml\n")


if __name__ == "__main__":
    home(); about(); team(); projects(); investors(); news(); contact(); members()
    for s, n, _ in PROJECTS:
        project_page(s, n)
    for s, t in [("privacy", "Privacy Policy"), ("cookies", "Cookie Policy"), ("terms", "Terms of Use")]:
        legal(s, t)
    seo()
    print("built")
