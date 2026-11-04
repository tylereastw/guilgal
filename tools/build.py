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
from datetime import date
from html import escape
import shutil
import subprocess
from pathlib import Path
import re
import segno
import hashlib
import json

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://www.guilgal.org"
EMAIL = "john@guilgal.org"
MEDIA = "members/media/"   # project-only images, served behind the partner login
QR_SALT = "gi-qr-7f3c9a1e"  # QR image names are hashed so they do not reveal project names
LEGAL = "Guilgal International is a trading name of Britcom Trading Limited, registered in England and Wales, company number 15625520."
IMG = "public/images/v2/"
DISCLAIMER = ("Guilgal International does not provide investment, financial or legal advice. "
              "Nothing on this site is an offer or solicitation.")
INDICATIVE = "Information is indicative and subject to technical review and agreement."


def e(s):
    return escape(s, quote=True)


# ---------------------------------------------------------------- icons (24px line icons)
ICONS = {
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "lock": '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
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
    ("Investors", "investors/"),
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
    q = segno.make(SITE + "/" + path, error="m")
    q.save(str(out), scale=6, dark="#10291F", light=None, border=0)
    q.save(str(out.with_suffix(".png")), scale=12, dark="#10291F", light="#FFFFFF", border=3)
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
      <div class="footer__logins">
        <a class="footer__login" href="{p}login/" data-when="partner-out">{ico("lock")} Partner login</a>
        <span class="footer__signed" data-when="partner-in" hidden><a class="footer__login footer__login--on" href="{p}members/">{ico("people")} Partner portal</a><button type="button" class="footer__login" data-footer-logout="partner">Log out</button></span>
        <a class="footer__login" href="{p}admin/" data-when="admin-out">{ico("lock")} Admin login</a>
        <span class="footer__signed" data-when="admin-in" hidden><a class="footer__login footer__login--on" href="{p}admin/">{ico("gear")} Admin panel</a><button type="button" class="footer__login" data-footer-logout="admin">Log out</button></span>
      </div>
    </div>
    <div class="wrap footer__bottom">
      <p class="footer__disclaimer">{DISCLAIMER}</p>
      <p>{LEGAL} <a href="{p}privacy/">Privacy</a> · <a href="{p}cookies/">Cookies</a> · <a href="{p}terms/">Terms</a> · <a href="{p}cookies/" data-cookie-settings>Cookie settings</a></p>
    </div>
  </footer>'''


def page(path, title, desc, active, body, p, noindex=False, scripts=()):
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
  <link rel="icon" href="{p}public/images/Guilgal_Favicon.ico" sizes="any">
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
  <script src="{p}js/main.js"></script>{"".join(f'<script src="{p}{x}"></script>' for x in scripts)}{"" if noindex else f'<script src="{p}js/consent.js"></script>'}
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
        f'''<li class="pcard" data-slug="{s}"><a href="{p}members/projects/{s}/" rel="nofollow">
          <div class="pcard__photo"><img src="{p}{IMG}card-{s}.jpg" alt="" loading="lazy"></div>
          <div class="pcard__body"><strong>{e(n)}</strong><span>{e(c)}</span><i class="arrow-circle">{ico("arrow")}</i></div>
          </a></li>''' for s, n, c in PROJECTS) + "</ul>"


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


def enquiry_form(p, title="Send Us a Message", projects=True, name="contact"):
    areas = ["Copper and gold", "Tantalum, tin and critical minerals", "Gold", "Energy and infrastructure", "Partner access request", "General partnership enquiry"]
    opts = "".join(f'<option>{e(a)}</option>' for a in areas)
    area = (f'<label class="field"><span>Area of interest*</span><select name="interest" required><option value="">Select an area</option>'
            f'{opts}</select></label>') if projects else ""
    org = ('<div class="form__row"><label class="field"><span>Organisation</span><input name="organisation" autocomplete="organization"></label>'
           '<label class="field"><span>Country</span><input name="country" autocomplete="country-name"></label></div>') if projects else ""
    return f'''<div class="formcard"><h3 class="formcard__head">{title}</h3>
        <form class="form" name="{name}" method="POST" action="{p}thanks/" data-netlify="true" netlify-honeypot="company_website" novalidate data-form>
          <input type="hidden" name="form-name" value="{name}">
          <p class="sr"><label>Leave this empty <input name="company_website" tabindex="-1" autocomplete="off"></label></p>
          <div class="form__row"><label class="field"><span>Name*</span><input name="name" autocomplete="name" required></label>
          <label class="field"><span>Email*</span><input type="email" name="email" autocomplete="email" required></label></div>
          {org}{area}
          <label class="field"><span>Your enquiry*</span><textarea name="message" rows="4" required></textarea></label>
          {consent(p)}
          <p class="form__msg" role="alert" hidden></p>
          <button class="btn btn--gold" type="submit">Submit enquiry {ico("arrow")}</button>
        </form></div>'''


def contact_block(p, form="contact"):
    return f'''    <section class="section" id="contact-us">
      <div class="wrap contact2">
        <div>
          <div class="shead"><h2>Get in Touch</h2></div>
          <p class="lead">We welcome enquiries from investors, partners and strategic collaborators worldwide.</p>
          <ul class="contact-list"><li>{dot("mail")}<div><strong>Email us</strong><a href="mailto:{EMAIL}">{EMAIL}</a></div></li></ul>
          <p class="small" style="margin-top:18px">{LEGAL}</p>
        </div>
        {enquiry_form(p, name=form)}
      </div>
    </section>
'''


# ---------------------------------------------------------------- pages
def home():
    p = ""
    inner = f'''<p class="hero__eyebrow">Mineral Exploration &amp; Strategic Development</p>
          <h1>Unlocking Africa's<br>Mineral Potential</h1>
          <p class="hero__sub">Connecting high-potential mineral projects with technical expertise, development partners and international partnerships.</p>
          <div class="hero__actions"><a class="btn btn--gold" href="about/">Discover More {ico("arrow")}</a><a class="btn btn--line" href="investors/#enquiry">Investor Enquiries {ico("arrow")}</a></div>'''
    strengths = [("doc", "Extensive Geological Data Analysis", "Detailed review of existing geological records to guide exploration."),
                 ("pick", "Field Reconnaissance and Sampling", "Direct field investigations to verify mineral prospects."),
                 ("handshake", "Strategic Connections", "Introductions between project owners, technical specialists and international partners.")]
    minerals = ["Copper", "Lithium", "Tantalum", "Tin", "Niobium", "Wolframite"]
    body = hero(p, "home-hero.jpg", inner, "hero--home") + strip([
        ("cubes", "Copper & Gold", "Exploration opportunities"),
        ("crystal", "Critical Minerals", "Strategic resources"),
        ("handshake", "Strategic Partnerships", "Lasting value")]) + f'''
    <section class="section">
      <div class="wrap grid-2">
        <div>
          <p class="label">Who we are</p>
          <h2>Combining Data and Fieldwork with Expert Insight</h2>
          <p class="lead">By bringing together extensive historic geological records with targeted field reconnaissance, sampling and small-scale drilling, Guilgal International helps develop the evidence needed to unlock the potential of mineral projects in the Democratic Republic of the Congo, Ghana and across Africa.</p>
          <p class="lead">We work with a network of engineers, geologists and field-based staff in the DRC, alongside local project owners and international partners.</p>
          <a class="btn btn--dark" href="about/">Learn More {ico("arrow")}</a>
        </div>
        <div class="photo"><img src="{IMG}about-who.jpg" alt="Rocky outcrop above a wide green valley and table mountains" loading="lazy"></div>
      </div>
    </section>

    <section class="section section--dark on-dark">
      <div class="wrap">
        <p class="label">Track record</p>
        <ul class="stats">
          <li><b>10+</b><strong>Years Experience</strong><span>More than ten years in mining project identification, development and geological consulting across the Democratic Republic of the Congo.</span></li>
          <li><b>10+</b><strong>Projects Advanced</strong><span>More than ten mining projects advanced by linking evidence-based exploration with capable partners, including listed companies in Australia and London.</span></li>
          <li><b>ASX · AIM</b><strong>Listed-Company Partners</strong><span>Projects identified for companies listed in Australia and London.</span></li>
        </ul>
      </div>
    </section>

    <section class="section section--cream2">
      <div class="wrap">
        <div class="shead"><h2>Key Strengths Driving Successful Mining Ventures</h2></div>
        <p class="lead">Our expertise spans data analysis, fieldwork and strategic connections to advance mining opportunities with clear evidence and trusted partnerships.</p>
        <ul class="cols4 cols3">{"".join(f"<li>{dot(i, True)}<h3>{t}</h3><p>{d}</p></li>" for i, t, d in strengths)}</ul>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <p class="label">Our approach</p>
        {approach_row()}
      </div>
    </section>

    <section class="section section--cream2" id="team">
      <div class="wrap">
        <div class="shead"><h2>Meet the Team</h2></div>
        <p class="lead">The people behind Guilgal International's project origination, partnerships and development activities across Africa.</p>
        <ul class="people people--home">{"".join(f'''<li class="person"><a href="about/team/">
          <div class="person__photo"><img src="{IMG}{t["photo"]}" alt="Portrait of {e(t["name"])}" style="object-position:{t.get("pos", "50% 25%")}" loading="lazy"></div>
          <div class="person__head"><h3>{e(t["name"])}</h3><p class="person__role">{e(t["role"])}</p></div>
          <div class="person__body"><p>{e(t["short"])}</p><span class="person__more">View profile {ico("arrow")}</span></div></a></li>''' for t in TEAM)}</ul>
      </div>
    </section>


    <section class="band">
      <div class="band__bg"><img src="{IMG}about-hero.jpg" alt=""></div>
      <div class="wrap band__grid">
        <div><p class="label">Start a conversation</p><h2>Start Developing Your Mining Project with Guilgal International</h2>
          <p>Engage with Guilgal International's experienced team to investigate, develop and advance promising mineral projects with confidence and precision.</p>
          <ul class="pills">{"".join(f'<li><span class="pill">{m}</span></li>' for m in minerals)}</ul>
          <div class="hero__actions"><a class="btn btn--gold" href="contact/">Contact Us {ico("arrow")}</a><a class="btn btn--line" href="investors/#enquiry">Investor Enquiries {ico("arrow")}</a></div></div>
        <aside class="qr"><div><p class="qr__title">Talk to John Boardman</p><p>Director, Guilgal International. Discuss mining services and project development needs in the DRC.</p><a class="btn btn--gold btn--sm" href="mailto:{EMAIL}">{EMAIL}</a></div></aside>
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
          <a class="btn btn--gold" href="{p}about/team/">Meet the Team {ico("arrow")}</a>'''
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
      </div>
    </section>
'''
    page("about/", "About | Guilgal International",
         "Guilgal International is a project development and strategic facilitation business advancing mineral opportunities in the DRC, Ghana and across Africa.",
         "About", body, p)


TEAM = [
    dict(name="John Boardman", role="Director, Guilgal International",
         sub="Former CEO, 1620 Capital | International Mining Investment & Corporate Development", photo="team-john.jpg", pos="50% 17%",
         short="Corporate strategy, international partnerships, investor relations and commercial project development.",
         bio=["John Boardman is responsible for Guilgal International's corporate strategy, international partnerships, investor relations and commercial project development.",
              "He has extensive experience in the mining sector, including his previous role as Chief Executive Officer of 1620 Capital in Perth, Western Australia, where he was involved in identifying, structuring and advancing mineral resource opportunities with ASX- and AIM-listed companies.",
              "John focuses on connecting African mineral opportunities with international partners, technical expertise and development capital."],
         keys=[("handshake", "Strategic partnerships"), ("people", "Investor engagement"), ("chart", "Corporate development"), ("target", "Project origination and transaction support")]),
    dict(name="Gedeon Ngoy Makonga Pelesa", role="DRC Project Partner", sub="Geological Coordination | Project Development", photo="team-gedeon.jpg",
         short="Local knowledge, project coordination and geological engagement across key mineral opportunities in the DRC.",
         bio=["Gedeon Ngoy Makonga Pelesa supports Guilgal International's project activities in the Democratic Republic of the Congo, contributing extensive local knowledge, project coordination and geological engagement across key mineral opportunities.",
              "He has significant experience in exploration, project identification and liaison with local authorities, technical teams and community stakeholders, with a focus on responsible and sustainable development.",
              "Gedeon plays a key role in advancing Guilgal International's mineral projects, including copper, gold, tantalum, tin and critical minerals, and coordinates field activities, technical studies and local partnerships."],
         keys=[("pick", "Geological coordination"), ("map", "Project identification and evaluation"), ("people", "Local partnerships and stakeholder engagement"), ("leaf", "Field activities and technical support")]),
    dict(name="Didier", role="Project Partner", sub="Business Development | Strategic Relationships", photo="team-didier.jpg",
         short="In-country relationships, commercial coordination and project development support in the DRC.",
         bio=["Didier contributes to Guilgal International's in-country relationships, commercial coordination and project development support in the Democratic Republic of the Congo.",
              "He plays an important role in business development, government and stakeholder engagement, and the facilitation of strategic partnerships across Guilgal International's project portfolio.",
              "Didier's local expertise and extensive network support the advancement of mineral and infrastructure opportunities, helping to create long-term value through collaboration and responsible development."],
         keys=[("handshake", "Business development"), ("people", "Government and stakeholder engagement"), ("chart", "Strategic partnerships"), ("gear", "Project coordination and commercial support")]),
]


def team():
    p = "../../"
    inner = '''<p class="label label--light">Our people</p><h1>Meet the Team</h1>
          <p class="hero__sub">The people behind Guilgal International's project origination, partnerships and development activities across Africa.</p>'''
    cards = []
    for t in TEAM:
        photo = f'<img src="{p}{IMG}{t["photo"]}" alt="Portrait of {e(t["name"])}" style="object-position:{t.get("pos", "50% 25%")}">' if t["photo"] else f'<b aria-hidden="true">{e(t["name"][0])}</b>'
        keys = "".join(f"<li>{ico(i)}{e(k)}</li>" for i, k in t["keys"])
        cards.append(f'''<li class="person">
          <div class="person__photo">{photo}</div>
          <div class="person__head"><h2>{e(t["name"])}</h2><p class="person__role">{e(t["role"])}</p><p class="person__sub">{e(t["sub"])}</p></div>
          <div class="person__body">{"".join(f"<p>{e(b)}</p>" for b in t["bio"])}<h3>Key areas</h3><ul class="keys">{keys}</ul></div>
        </li>''')
    values = [("people", "International experience"), ("africa", "Local knowledge"), ("handshake", "Strategic partnerships"), ("chart", "Project development"), ("leaf", "Responsible growth")]
    body = hero(p, "team-hero.jpg", inner) + f'''    <section class="strip"><ul class="values">{"".join(f"<li>{ico(i)}<span>{t}</span></li>" for i, t in values)}</ul></section>
''' + f'''
    <section class="section"><div class="wrap"><ul class="people">{"".join(cards)}</ul>
</div></section>

    <section class="band">
      <div class="band__bg"><img src="{p}{IMG}about-river.jpg" alt=""></div>
      <div class="wrap band__grid"><div><blockquote class="band__quote">"International connections, local expertise and shared commitment to responsible development."</blockquote>
        <ul class="trow trow--band">{"".join(f"<li>{ico(i)}<span>{t}</span></li>" for i, t in [("leaf", "Partnerships that create value"), ("people", "Projects that support local communities"), ("globe", "Responsible development for a sustainable future")])}</ul></div></div>
    </section>
'''
    page("about/team/", "Meet the Team | Guilgal International", "The people behind Guilgal International.", "About", body, p)


def investors():
    p = "../"
    inner = f'''<h1>Investor Centre &amp; Contact</h1>
          <p class="hero__meta">Partner with Guilgal International: Unlock the Value of Africa</p>
          <p class="hero__sub">Find out how we partner, request access to private project information and get in touch with our team.</p>
          <ul class="pills"><li><a class="pill" href="#why">Why partner with us</a></li><li><a class="pill" href="#access">Partner access</a></li><li><a class="pill" href="#enquiry">Contact us</a></li></ul>'''
    why = [("diamond", "Vetted Opportunities", "Projects are reviewed before they are introduced to partners."),
           ("handshake", "Local Relationships", "Established working relationships with project owners and stakeholders."),
           ("people", "Technical Networks", "Access to geological, technical and commercial specialists."),
           ("leaf", "Responsible Development", "A focus on responsible, structured project progression."),
           ("chart", "Long-Term Partnerships", "Durable relationships rather than single transactions.")]
    body = hero(p, "investors-hero.jpg", inner) + f'''
    <section class="section" id="why">
      <div class="wrap">
        <div class="shead"><h2>Why Partner with Guilgal International?</h2></div>
        <p class="lead">Guilgal International brings together vetted opportunities, local relationships and technical expertise, so partners can engage with African projects in a structured, responsible way.</p>
        <ul class="why-row">{"".join(f"<li>{dot(i, True)}<strong>{t}</strong><span class='why-row__text'>{d}</span></li>" for i, t, d in why)}</ul>
        <div class="quote-band"><img src="{p}{IMG}africa-gold.jpg" alt=""><blockquote>"Together we can unlock Africa's mineral and energy potential."</blockquote></div>
      </div>
    </section>

    <section class="section section--cream2" id="access">
      <div class="wrap">
        <div class="access-head">
          <div><div class="shead"><h2>Partner Access</h2></div>
            <p class="lead">Project information, maps, technical summaries and milestones are private. Each project has its own password-protected page, shared directly with invited partners.</p></div>
          <a class="btn btn--gold" href="#enquiry">Request access {ico("arrow")}</a>
        </div>
        <ol class="steps steps--row">
          <li><b>1</b><strong>Make an enquiry</strong><span>Tell us about your organisation and the opportunities you are interested in.</span></li>
          <li><b>2</b><strong>Confidentiality agreement</strong><span>We send a confidentiality agreement for signature.</span></li>
          <li><b>3</b><strong>Approval</strong><span>Once signed and approved, we send the project link and access details.</span></li>
        </ol>
      </div>
    </section>
''' + contact_block(p, "investor-enquiry").replace('id="contact-us"', 'id="enquiry"') + f'''
    <section class="band">
      <div class="band__bg"><img src="{p}{IMG}about-hero.jpg" alt=""></div>
      <div class="wrap band__grid">
        <div><h2 class="band__quote">Building a Sustainable Future with Guilgal International</h2>
          <p>Next steps: discuss partnering with us and join us as we grow in Africa.</p></div>
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
    body = hero(p, "about-river.jpg", inner) + f'''
    <section class="section">
      <div class="wrap">
        <div class="filters" role="group" aria-label="Filter updates">
          <div class="chips"><button type="button" class="chip is-on" data-kind="all" aria-pressed="true">All</button><button type="button" class="chip" data-kind="news" aria-pressed="false">News</button><button type="button" class="chip" data-kind="insight" aria-pressed="false">Insights</button></div>
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
    inner = '''<p class="label label--light">Partner access</p><h1>Partner Portal</h1>
          <p class="hero__sub">Private project information for invited partners. Please do not share these pages or their links.</p>
          <p class="portal__who" data-me hidden></p>
          <div class="hero__actions"><button class="btn btn--line" type="button" data-logout>Sign out</button></div>'''
    body = hero(p, "home-hero.jpg", inner) + f'''
    <section class="section"><div class="wrap">
      <div class="shead"><h2>Your Projects</h2></div>
      <p class="lead">{INDICATIVE}</p>
      <div data-portal>{project_cards(p)}</div>
      <p class="small" data-none hidden>No projects have been assigned to your account yet. Please contact <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
    </div></section>
'''
    page("members/", "Partner Portal | Guilgal International", "Private partner portal.", "", body, p, noindex=True)


def login():
    p = "../"
    inner = '''<p class="label label--light">Partner access</p><h1>Partner Login</h1>
          <p class="hero__sub">Sign in to view the projects shared with you.</p>'''
    body = hero(p, "home-hero.jpg", inner) + f'''
    <section class="section"><div class="wrap grid-2" style="align-items:start">
      <div><h2>Sign in</h2><p class="lead">Use the email address and password sent to you by Guilgal International. You stay signed in on this device for 30 days.</p>
        <p class="lead">No account yet? Access is by invitation after a confidentiality agreement.</p>
        <a class="btn btn--line-dark" href="{p}investors/#enquiry">Request access {ico("arrow")}</a></div>
      <div class="formcard"><h3 class="formcard__head">Partner login</h3>
        <form class="form" data-login novalidate>
          <label class="field"><span>Email*</span><input type="email" name="email" autocomplete="username" required></label>
          <label class="field"><span>Password*</span><input type="password" name="password" autocomplete="current-password" required></label>
          <p class="form__msg" role="alert" hidden></p>
          <button class="btn btn--gold" type="submit">Sign in {ico("arrow")}</button>
          <p class="small">Forgotten your password? Email <a href="mailto:{EMAIL}?subject=Partner%20login">{EMAIL}</a> and we will reset it.</p>
        </form></div>
    </div></section>
'''
    page("login/", "Partner Login | Guilgal International", "Partner sign in.", "", body, p, noindex=True)


def admin():
    p = "../"
    body = f'''    <section class="section admin"><div class="wrap">
      <h1>Partner Access Admin</h1>
      <div data-admin-setup hidden>
        <div class="formcard" style="max-width:560px"><h3 class="formcard__head">First-time setup: authenticator</h3>
          <form class="form" data-setup-start novalidate>
            <p class="small">Admin sign-in uses the admin password plus a 6-digit code from an authenticator app on your phone (Google Authenticator, Microsoft Authenticator or 1Password). This is done once.</p>
            <label class="field"><span>Admin password*</span><input type="password" name="password" autocomplete="current-password" required></label>
            <p class="form__msg" role="alert" hidden></p>
            <button class="btn btn--gold" type="submit">Continue {ico("arrow")}</button>
          </form>
          <form class="form" data-setup-confirm hidden novalidate>
            <p class="small"><strong>1.</strong> In your authenticator app, tap + and scan this code.</p>
            <div class="setup-qr" data-setup-qr></div>
            <p class="small">Can't scan? Choose "Enter a setup key" and type: <code data-setup-key></code></p>
            <p class="small"><strong>2.</strong> Enter the 6-digit code the app now shows for Guilgal International.</p>
            <label class="field"><span>Authenticator code*</span><input name="code" inputmode="numeric" maxlength="6" autocomplete="one-time-code" required></label>
            <p class="form__msg" role="alert" hidden></p>
            <button class="btn btn--gold" type="submit">Finish setup {ico("arrow")}</button>
          </form></div>
      </div>
      <div data-admin-login hidden>
        <div class="formcard" style="max-width:460px"><h3 class="formcard__head">Admin sign in</h3>
          <form class="form" data-admin-signin novalidate>
            <label class="field"><span>Admin password*</span><input type="password" name="password" autocomplete="current-password" required></label>
            <label class="field"><span>Authenticator code*</span><input name="code" inputmode="numeric" pattern="[0-9]{{6}}" maxlength="6" autocomplete="one-time-code" required></label>
            <p class="form__msg" role="alert" hidden></p>
            <button class="btn btn--gold" type="submit">Sign in {ico("arrow")}</button>
          </form></div>
      </div>
      <div data-admin-app hidden>
        <div class="adm-bar">
          <div class="adm-tabs" role="tablist">
            <button type="button" role="tab" class="adm-tab is-on" data-tab="partners" aria-selected="true">{ico("people")} Partners</button>
            <button type="button" role="tab" class="adm-tab" data-tab="links" aria-selected="false">{ico("map")} Project links &amp; QR codes</button>
            <button type="button" role="tab" class="adm-tab" data-tab="briefs" aria-selected="false">{ico("doc")} Project briefs</button>
          </div>
          <button class="btn btn--line-dark btn--sm" type="button" data-admin-logout>Sign out</button>
        </div>

        <div class="adm-panel" data-panel="partners">
          <div class="adm-head">
            <div><h2>Partners</h2><p class="small">Everyone who can sign in to the partner portal, and the projects each one can see.</p></div>
            <button class="btn btn--gold" type="button" data-add>+ Add partner</button>
          </div>
          <div class="adm-tools">
            <p class="adm-stats" data-stats></p>
            <label class="adm-search"><span class="sr-only">Search partners</span>{ico("search")}<input type="search" placeholder="Search by name, email or project" data-search></label>
          </div>
          <ul class="ulist" data-users></ul>
          <details class="adm-help"><summary>How partner access works</summary>
            <ol>
              <li><b>Add partner</b>: enter their email and tick the projects they may see. A secure password is created for you.</li>
              <li><b>Invitation</b>: create a ready-to-send invitation with the sign-in link, their login details, step-by-step instructions and a QR code for each project. Copy it into an email or save it as a PDF.</li>
              <li><b>Edit</b> to change their projects or reset their password. <b>Pause</b> blocks access without deleting the account; <b>Delete</b> removes it.</li>
            </ol></details>
        </div>

        <div class="adm-panel" data-panel="links" hidden>
          <div class="adm-head"><div><h2>Project links &amp; QR codes</h2><p class="small">Each link opens the project page after the partner signs in. Anyone without access is taken to the login screen first. Invitations include these automatically.</p></div></div>
          <ul class="qrs" data-qrs></ul>
        </div>

        <div class="adm-panel" data-panel="briefs" hidden>
          <div class="adm-head"><div><h2>Project briefs</h2><p class="small">Briefs are generated automatically from each project page every time the site is built, so they always match the page. Nothing needs uploading.</p></div></div>
          <ul class="briefs" data-briefs></ul>
        </div>
      </div>

      <dialog class="adm-dialog" data-user-dialog aria-labelledby="udlg-title">
        <div class="adm-dialog__head"><h3 id="udlg-title" data-form-title>Add a partner</h3><button type="button" class="adm-x" data-close aria-label="Close">&times;</button></div>
        <form class="form pform" data-user-form novalidate>
          <div class="form__row">
            <label class="field"><span>Email address*</span><input type="email" name="email" required></label>
            <label class="field"><span>Name</span><input name="name" placeholder="For example, Jane Smith"></label>
          </div>
          <fieldset class="checks">
            <legend>Which projects can they see?</legend>
            <label class="check check--all"><input type="checkbox" name="projects" value="*"><span>All projects, including any added later</span></label>
            <div class="checks__list" data-project-checks></div>
          </fieldset>
          <fieldset class="checks">
            <legend>Password</legend>
            <label class="check" data-only-edit hidden><input type="radio" name="pwmode" value="keep"><span>Keep their current password</span></label>
            <label class="check"><input type="radio" name="pwmode" value="generate" checked><span data-gen-label>Create a secure password for me</span></label>
            <label class="check"><input type="radio" name="pwmode" value="choose"><span>Let me type a password</span></label>
            <label class="field" data-choose hidden><span>Password (at least 10 characters)</span><input name="password" autocomplete="new-password"></label>
            <p class="small" data-only-edit hidden>A new password signs the partner out on all their devices.</p>
          </fieldset>
          <label class="check switch" data-only-edit hidden><input type="checkbox" name="active" checked><span>Account active (untick to pause access without deleting)</span></label>
          <p class="form__msg" role="alert" hidden></p>
          <div class="pform__actions"><button class="btn btn--gold" type="submit" data-submit-label>Add partner {ico("arrow")}</button><button class="btn btn--line-dark" type="button" data-close>Cancel</button></div>
        </form>
        <div class="details" data-details hidden>
          <p class="details__ok" data-details-title>Partner added</p>
          <p class="small">Send them their invitation now. The password is shown only once.</p>
          <pre data-details-text></pre>
          <div class="pform__actions"><button class="btn btn--gold" type="button" data-details-invite>Create invitation {ico("arrow")}</button><button class="btn btn--sm btn--line-dark" type="button" data-copy-details>Copy details</button><button class="btn btn--sm btn--line-dark" type="button" data-close>Done</button></div>
        </div>
      </dialog>

      <dialog class="adm-dialog adm-dialog--sm" data-invite-dialog aria-labelledby="idlg-title">
        <div class="adm-dialog__head"><h3 id="idlg-title">Invitation for <span data-invite-who></span></h3><button type="button" class="adm-x" data-close aria-label="Close">&times;</button></div>
        <div class="pform">
          <p>For security, passwords are never stored in a readable form, so an invitation can only show a password that is created now.</p>
          <div class="pform__actions pform__actions--stack">
            <button class="btn btn--gold" type="button" data-invite-new>Create a new password and invitation {ico("arrow")}</button>
            <button class="btn btn--line-dark" type="button" data-invite-nopw>Invitation without password (send it separately)</button>
          </div>
          <p class="small">A new password replaces their current one and signs them out on other devices.</p>
          <p class="form__msg" role="alert" hidden></p>
        </div>
      </dialog>
    </div></section>
'''
    page("admin/", "Admin | Guilgal International", "Admin.", "", body, p, noindex=True, scripts=["js/admin.js"])


def thanks():
    p = "../"
    body = hero(p, "about-hero.jpg", '''<h1>Thank you</h1><p class="hero__sub">Your message has been sent. We will be in touch.</p>
          <a class="btn btn--gold" href="../">Back to home</a>''')
    page("thanks/", "Thank you | Guilgal International", "Message sent.", "", body, p, noindex=True)

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
                ("handshake", "Guilgal International role: commercial facilitation and introductions"), ("chart", "Opportunity for regional power supply, mining and industrial growth"),
                ("leaf", "Positive environmental and social impact"), ("globe", "Potential for long-term partnerships and investment")],
    sites=[("Kilubi Hydropower Project", "Haut-Lomami Province", "kilubi",
            ["Located in Haut-Lomami Province", "Significant renewable energy potential", "Government and Ministry engagement", "Supports local communities and regional development", "Positive environmental and social impact"],
            [("Government engagement", "In progress"), ("Feasibility studies", "Planned"), ("Financing discussions", "Planned"), ("Approvals and permits", "Planned"), ("Construction and development", "Subject to funding")]),
           ("Haut-Katanga Hydropower Projects", "Three dams | Haut-Katanga Province", "katanga",
            ["Three hydropower projects in Haut-Katanga", "Early-stage development and feasibility discussions", "Ministry of Energy and Hydropower engagement", "Opportunity to supply power to mining and industrial operations", "Open to international infrastructure partners"],
            [("Project identification and validation", ""), ("Feasibility studies", "Planned"), ("Financing discussions", "Planned"), ("Approvals and permits", "Planned"), ("Construction and development", "Subject to funding")])],
    figures=[], gallery_title="Typical hydropower infrastructure",
    gallery=[("dam", "Dam and spillway (infrastructure)"), ("turbine", "Turbine and generator (power generation)"), ("transmission", "Transmission infrastructure (regional supply)")],
    timeline=[("Q4 2026", "Government agreements and mandates"), ("Q1 2027", "Detailed studies and feasibility support"), ("Q2 to Q3 2027", "Financing discussions and partner development"), ("2028+", "Construction (subject to approvals and funding)"), ("2030+", "Operational power supply")],
    timeline_note="Timeline is indicative and subject to government approvals, partner commitments, financing and regulatory processes.",
    benefits=[("leaf", "Clean and renewable energy supply"), ("chart", "Supports mining and industrial development"), ("people", "Local employment and skills development"),
              ("gear", "Improved infrastructure and living standards"), ("leaf", "Reduced carbon emissions"), ("globe", "Long-term economic growth in the region")],
    programme=[],
    role=True,
    opportunity="We welcome discussions with infrastructure investors, development partners and energy offtakers interested in the Kilubi and Haut-Katanga projects, working alongside SHE-QMS and government."),
}


def project_page(slug, card_name):
    d = PDATA[slug]
    p = "../../../"
    path = f"members/projects/{slug}/"
    meta = ' <span>|</span> '.join(e(m) for m in d["meta"])
    sub = f'<p class="hero__meta">{e(d["sub"])}</p>' if d.get("sub") else ""
    inner = f'''<a class="back" href="{p}members/">{ico("back")} Partner portal</a>
          <h1>{e(d["title"])}</h1>{sub}
          <p class="hero__meta">{meta}</p>
          <p class="hero__lead">{e(d["lead"])}</p>
          <ul class="pills">{"".join(f'<li><span class="pill">{e(x)}</span></li>' for x in d["pills"])}</ul>
          <div class="hero__actions"><a class="btn btn--gold" href="brief.pdf" download>{ico("doc")} Download project brief</a><a class="btn btn--line" href="mailto:{EMAIL}?subject={e(card_name)}">Contact us {ico("arrow")}</a></div>'''
    body = hero(p, f"{slug}-hero.jpg", inner, "hero--page")
    if d.get("facts"):
        body += '    <section class="factbar"><ul class="factbar__list">' + "".join(
            f"<li>{dot(i)}<div><strong>{e(t)}</strong><span>{e(s)}</span></div></li>" for i, t, s in d["facts"]) + "</ul></section>\n"
    role = '<p class="role-note">Guilgal International\'s role on this project is commercial facilitation and introductions only.</p>' if d.get("role") else ""
    note = f'<p class="draft">{e(d["note"])}</p>' if d.get("note") else ""
    body += f'''
    <section class="section section--tight">
      <div class="wrap">
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
    if figs:
        body += f'    <section class="section section--tight section--cream2"><div class="wrap {cols}" style="align-items:start">{"".join(figs)}</div></section>\n'
    for st, sub_, img, bl, status in d.get("sites", []):
        body += f'''    <section class="section section--tight section--cream2"><div class="wrap site">
      <div><p class="label">{e(st)}</p><p class="site__sub">{e(sub_)}</p><img class="photo" src="{p}{IMG}{slug}-{img}.jpg" alt="{e(st)}" loading="lazy">
        <ul class="bullets">{"".join(f"<li>{e(x)}</li>" for x in bl)}</ul></div>
      <div><p class="label">Project status (indicative)</p><ol class="steps">{"".join(f"<li><b>{i}</b><strong>{e(a)}</strong><span>{e(b)}</span></li>" for i, (a, b) in enumerate(status, 1))}</ol></div>
    </div></section>
'''
    gal = d.get("gallery", [])
    if gal:
        gt = f'<p class="label">{e(d["gallery_title"])}</p>' if d.get("gallery_title") else ""
        body += ('    <section class="section section--tight"><div class="wrap">' + gt + '<div class="gallery" style="grid-template-columns:repeat(' + str(len(gal)) + ',1fr)">' +
                 "".join(f'<figure><img src="{p}{IMG}{slug}-{g}.jpg" alt="{e(c)}" loading="lazy"><figcaption>{e(c)}</figcaption></figure>' for g, c in gal) + "</div></div></section>\n")
    prog = "".join(f'<li><b>{i}</b><strong>{e(t)}</strong><span>{e(s)}</span></li>' for i, (t, s) in enumerate(d["programme"], 1))
    tl = ""
    if d.get("timeline"):
        tl = (f'<div><p class="label">Indicative timeline</p><ol class="timeline" style="--n:{len(d["timeline"])}">' +
              "".join(f"<li><strong>{e(a)}</strong>{e(b)}</li>" for a, b in d["timeline"]) +
              f'</ol><p class="disclaim">{e(d.get("timeline_note", "Timeline is indicative and subject to funding, access, seasonal conditions and regulatory approvals."))}</p></div>')
    else:
        tl = '<div><p class="label">Indicative timeline</p><p class="disclaim">An indicative timeline will be added once it has been reviewed and approved.</p></div>'
    body += f'''    <section class="section section--tight">
      <div class="wrap grid-3" style="align-items:start">
        {f'<div><p class="label">{"Development pathway" if slug == "alpha" else "Next steps" if slug == "nizi-baluma" else "Exploration programme"}</p><ol class="steps">{prog}</ol></div>' if prog else ""}
        {f'<div><p class="label">Strategic benefits</p><ul class="benefits">' + "".join(f"<li>{dot(i)}<span>{e(t)}</span></li>" for i, t in d["benefits"]) + "</ul></div>" if d.get("benefits") else ""}
        {tl}
        <div class="opp"><p class="label">Partnership opportunity</p><div class="opp__text">{dot("handshake", True)}<p class="small">{e(d["opportunity"])}</p></div>
          <a class="btn btn--gold" href="{p}investors/#enquiry">Investor enquiries {ico("arrow")}</a>
          <a class="btn btn--dark" href="brief.pdf" download>Download project brief {ico("arrow")}</a>
          <p class="small">{INDICATIVE}</p></div>
      </div>
    </section>
'''
    body += f'''    <section class="section section--tight"><div class="wrap"><a class="backlink" href="{p}members/">{ico("back")} Back to the partner portal</a></div></section>
'''
    page(path, f"{d['title']} | Partner Access | Guilgal International", "Private project page.", "Projects", body, p, noindex=True)


BRIEF_CSS = """
@page { size: A4; margin: 12mm 0 10mm; }
@page :first { margin: 0 0 10mm; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; font: 9.6pt/1.5 "Open Sans", Arial, sans-serif; color: #13251D; background: #fff; }
h1, h2, h3 { font-family: "Montserrat", Arial, sans-serif; margin: 0; }
.cover { position: relative; height: 90mm; color: #fff; background: #10291F; overflow: hidden; }
.cover img.bg { position: absolute; right: 0; top: 0; width: 70%; height: 100%; object-fit: cover; }
.cover::before { content: ""; position: absolute; inset: 0; z-index: 1; background: linear-gradient(90deg, #10291F 28%, rgba(16,41,31,.85) 45%, rgba(16,41,31,.2) 80%); }
.cover .in { position: relative; z-index: 2; padding: 12mm 14mm; height: 100%; display: flex; flex-direction: column; }
.brandrow { display: flex; align-items: center; gap: 10px; }
.brandrow img { width: 15mm; height: 15mm; border-radius: 50%; object-fit: cover; }
.brandrow b { font: 700 15pt "Cinzel", Georgia, serif; color: #D7B46E; letter-spacing: .04em; display: block; line-height: 1; }
.brandrow span { font: 600 6.5pt "Montserrat", Arial, sans-serif; letter-spacing: .38em; display: block; margin-top: 3px; }
.tagline { font: 600 6pt "Montserrat", Arial, sans-serif; letter-spacing: .12em; color: rgba(255,255,255,.8); margin-top: 3px; }
.kicker { margin-top: auto; font: 700 7.5pt "Montserrat", Arial, sans-serif; letter-spacing: .14em; text-transform: uppercase; color: #D7B46E; }
.cover h1 { font-size: 27pt; line-height: 1.05; margin: 2mm 0 2mm; max-width: 120mm; }
.cover .meta { font: 500 11pt "Montserrat", Arial, sans-serif; margin-bottom: 3mm; }
.cover .meta i { color: #D7B46E; font-style: normal; padding: 0 6px; }
.cover .lead { font: 600 10pt/1.45 "Montserrat", Arial, sans-serif; color: #E8C77E; max-width: 115mm; margin: 0 0 3mm; }
.pills { display: flex; flex-wrap: wrap; gap: 5px; margin: 0; padding: 0; list-style: none; }
.pills li { border: 1px solid rgba(255,255,255,.8); border-radius: 20px; padding: 2px 9px; font: 600 6.5pt "Montserrat", Arial, sans-serif; letter-spacing: .06em; text-transform: uppercase; }
.page { padding: 8mm 14mm 0; }
.note { background: #FFF6E0; border-left: 3px solid #D7B46E; padding: 3mm 4mm; font-size: 8.4pt; margin-bottom: 5mm; }
.role { background: #10291F; color: #fff; padding: 3mm 4mm; font-weight: 600; margin-bottom: 4mm; }
.label { font: 700 8pt "Montserrat", Arial, sans-serif; letter-spacing: .1em; text-transform: uppercase; color: #9A7424; margin: 0 0 2.5mm; display: flex; align-items: center; gap: 8px; }
.label::after { content: ""; width: 14mm; height: 1px; background: #D7B46E; }
.cols { display: grid; grid-template-columns: 1.1fr 1fr; gap: 8mm; margin-bottom: 5mm; }
.cols3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6mm; margin-bottom: 6mm; }
.cols p { margin: 0 0 2.5mm; }
.hl { list-style: none; margin: 0; padding: 0; display: grid; gap: 2.2mm; }
.hl li { position: relative; padding-left: 6mm; }
.hl li::before { content: ""; position: absolute; left: 0; top: 1.2mm; width: 3mm; height: 3mm; border-radius: 50%; background: #10291F; box-shadow: inset 0 0 0 .8mm #D7B46E; }
.facts { display: grid; grid-template-columns: repeat(5, 1fr); gap: 3mm; margin-bottom: 6mm; padding: 3mm 0; border-top: 1px solid #E4DCCB; border-bottom: 1px solid #E4DCCB; }
.facts b { display: block; font: 700 7pt "Montserrat", Arial, sans-serif; text-transform: uppercase; }
.facts span { font-size: 7.4pt; color: #3F4A44; line-height: 1.3; display: block; }
figure { margin: 0; break-inside: avoid; }
figure img { width: 100%; height: 34mm; object-fit: cover; border-radius: 2px; display: block; }
figure.map img { height: 56mm; }
figcaption { font-size: 7pt; color: #3F4A44; margin-top: 1mm; }
.bul { list-style: none; margin: 2mm 0 0; padding: 0; }
.bul li { position: relative; padding-left: 4mm; font-size: 8.2pt; margin-bottom: 1mm; }
.bul li::before { content: ""; position: absolute; left: 0; top: 1.4mm; width: 1.8mm; height: 1.8mm; border-radius: 50%; border: .5mm solid #D7B46E; }
table { width: 100%; border-collapse: collapse; font-size: 8pt; }
th { background: #10291F; color: #fff; text-align: left; padding: 1.4mm 2mm; font: 600 7.4pt "Montserrat", Arial, sans-serif; }
td { padding: 1.2mm 2mm; border-bottom: 1px solid #E4DCCB; }
td:first-child { font-weight: 700; }
.steps { list-style: none; margin: 0; padding: 0; counter-reset: s; display: grid; gap: 2mm; }
.steps li { counter-increment: s; position: relative; padding-left: 8mm; min-height: 6mm; }
.steps li::before { content: counter(s); position: absolute; left: 0; top: 0; width: 5.6mm; height: 5.6mm; border-radius: 50%; background: #D7B46E; color: #10291F; font: 700 8pt/5.6mm "Montserrat", Arial, sans-serif; text-align: center; }
.steps b { display: block; font: 700 8.4pt "Montserrat", Arial, sans-serif; }
.steps span { font-size: 8pt; color: #3F4A44; }
.tl { list-style: none; margin: 0 0 2mm; padding: 0; display: grid; gap: 1.6mm; }
.tl li { display: grid; grid-template-columns: 22mm 1fr; font-size: 8pt; }
.tl b { font: 700 8pt "Montserrat", Arial, sans-serif; }
.small { font-size: 7.4pt; color: #3F4A44; }
.keep { break-inside: avoid; }
.foot { margin-top: 4mm; background: #13251D; color: rgba(255,255,255,.85); padding: 4mm 14mm; font-size: 7.2pt; break-inside: avoid; }
.foot b { color: #D7B46E; font-family: "Montserrat", Arial, sans-serif; }
.foot p { margin: 0 0 1.5mm; }
"""


def brief_page(slug, card_name):
    """Print-designed HTML version of a project page; tools/briefs.mjs prints it to brief.pdf."""
    d = PDATA[slug]
    root = "../../../"
    img = lambda f: f"{root}{IMG}{f}"
    meta = "<i>|</i>".join(e(m) for m in d["meta"])
    sub = f'<p class="meta">{e(d["sub"])}</p>' if d.get("sub") else ""
    pills = "".join(f"<li>{e(x)}</li>" for x in d["pills"])
    facts = ("<div class='facts'>" + "".join(f"<div><b>{e(t)}</b><span>{e(x)}</span></div>" for _, t, x in d["facts"]) + "</div>") if d.get("facts") else ""
    role = "<p class='role'>Guilgal International's role on this project is commercial facilitation and introductions only.</p>" if d.get("role") else ""
    note = f"<p class='note'>{e(d['note'])}</p>" if d.get("note") else ""
    figs = []
    for title, im, cap, bullets in d["figures"]:
        bl = "<ul class='bul'>" + "".join(f"<li>{e(b)}</li>" for b in bullets) + "</ul>" if bullets else ""
        figs.append(f"<div class='keep'><p class='label'>{e(title)}</p><figure><img src='{img(slug + '-' + im + '.jpg')}' alt=''>{f'<figcaption>{e(cap)}</figcaption>' if cap else ''}</figure>{bl}</div>")
    for st, sub_, im, bl, status in d.get("sites", []):
        figs.append(f"<div class='keep'><p class='label'>{e(st)}</p><p class='small' style='margin:-1mm 0 2mm'>{e(sub_)}</p><figure><img src='{img(slug + '-' + im + '.jpg')}' alt=''></figure>"
                    "<ul class='bul'>" + "".join(f"<li>{e(x)}</li>" for x in bl) + "</ul>"
                    "<p class='label' style='margin-top:3mm'>Project status (indicative)</p><ol class='steps'>" +
                    "".join(f"<li><b>{e(a)}</b><span>{e(b)}</span></li>" for a, b in status) + "</ol></div>")
    table = ""
    if d.get("table"):
        tt, head, rows, tnote = d["table"]
        table = (f"<div class='keep'><p class='label'>{e(tt)}</p><table><thead><tr>" + "".join(f"<th>{h}</th>" for h in head) + "</tr></thead><tbody>" +
                 "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows) + f"</tbody></table><p class='small'>{e(tnote)}</p></div>")
        figs.append(table)
    grid = "cols3" if len(figs) >= 3 else "cols"
    gallery = ""
    if d.get("gallery"):
        n = min(len(d["gallery"]), 4)
        gallery = (f"<div class='keep' style='display:grid;grid-template-columns:repeat({n},1fr);gap:4mm;margin-bottom:6mm'>" +
                   "".join(f"<figure><img src='{img(slug + '-' + g + '.jpg')}' alt='' style='height:28mm'><figcaption>{e(c)}</figcaption></figure>" for g, c in d["gallery"][:4]) + "</div>")
    prog = ("<div class='keep'><p class='label'>" + ("Development pathway" if slug == "alpha" else "Next steps" if slug == "nizi-baluma" else "Exploration programme") +
            "</p><ol class='steps'>" + "".join(f"<li><b>{e(t)}</b>{f'<span>{e(x)}</span>' if x else ''}</li>" for t, x in d["programme"]) + "</ol></div>") if d.get("programme") else ""
    tl = ""
    if d.get("timeline"):
        tl = ("<div class='keep'><p class='label'>Indicative timeline</p><ul class='tl'>" + "".join(f"<li><b>{e(a)}</b><span>{e(b)}</span></li>" for a, b in d["timeline"]) +
              f"</ul><p class='small'>{e(d.get('timeline_note', 'Timeline is indicative and subject to funding, access, seasonal conditions and regulatory approvals.'))}</p></div>")
    benefits = ("<div class='keep'><p class='label'>Strategic benefits</p><ul class='hl'>" + "".join(f"<li>{e(t)}</li>" for _, t in d["benefits"]) + "</ul></div>") if d.get("benefits") else ""
    opp = f"<div class='keep'><p class='label'>Partnership opportunity</p><p>{e(d['opportunity'])}</p></div>"
    lower = [x for x in (prog, benefits, tl, opp) if x]
    generated = date.today().strftime("%-d %B %Y")
    html = f"""<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><title>{e(d['title'])}: Project Brief | Guilgal International</title>
<meta name="robots" content="noindex, nofollow, noarchive"><link rel="stylesheet" href="{root}css/fonts.css"><style>{BRIEF_CSS}</style></head><body>
<section class="cover"><img class="bg" src="{img(slug + '-hero.jpg')}" alt=""><div class="in">
  <div class="brandrow"><img src="{img('logo-emblem.jpg')}" alt=""><div><b>GUILGAL</b><span>INTERNATIONAL</span><div class="tagline">EXPLORATION | DEVELOPMENT | PARTNERSHIPS</div></div></div>
  <p class="kicker">Project brief · Confidential</p>
  <h1>{e(d['title'])}</h1>{sub}<p class="meta">{meta}</p>
  <p class="lead">{e(d['lead'])}</p><ul class="pills">{pills}</ul>
</div></section>
<main class="page">
  {role}{note}{facts}
  <div class="cols"><div><p class="label">Project overview</p>{''.join(f'<p>{e(x)}</p>' for x in d['overview'])}</div>
    <div><p class="label">Key highlights</p><ul class="hl">{''.join(f'<li>{e(t)}</li>' for _, t in d['highlights'])}</ul></div></div>
  <div class="cols"><figure class="map keep"><p class="label">Project location</p><img src="{img(slug + '-location.jpg')}" alt=""><figcaption>Illustrative location map</figcaption></figure>
    <div>{figs[0] if figs else ''}</div></div>
  {f'<div class="{grid}">' + ''.join(figs[1:]) + '</div>' if len(figs) > 1 else ''}
  {gallery}
  <div class="cols3">{''.join(lower)}</div>
</main>
<footer class="foot">
  <p><b>Contact Guilgal International</b> · John Boardman, Director · {EMAIL} · {SITE}</p>
  <p>{DISCLAIMER} {INDICATIVE}</p>
  <p>{LEGAL} Generated from the project page on {generated}.</p>
</footer></body></html>"""
    assert "—" not in html, f"em dash in brief {slug}"
    out = ROOT / f"members/projects/{slug}/brief.html"
    out.write_text(html)


def legal(slug, title):
    p = "../"
    body = hero(p, "about-river.jpg", f'<h1>{e(title)}</h1>') + f'''
    <section class="section"><div class="wrap" style="max-width:860px">
      <p class="placeholder">[{e(title)} to be supplied before launch.]</p>
      <p>{LEGAL} Contact: <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
      <p class="small">{DISCLAIMER}</p></div></section>
'''
    page(f"{slug}/", f"{title} | Guilgal International", f"{title} for Guilgal International.", "", body, p)


def cookie_policy():
    p = "../"
    rows = [
        ("gi_cookie_consent", "Guilgal International", "Essential", "Remembers your cookie choice (stored in your browser, not sent to us).", "12 months"),
        ("gi_session", "Guilgal International", "Essential", "Keeps invited partners signed in to the private partner portal.", "30 days"),
        ("gi_admin", "Guilgal International", "Essential", "Keeps Guilgal International administrators signed in to the admin panel.", "2 hours"),
        ("_clck, _clsk, CLID, ANONCHK, MR, MUID, SM", "Microsoft Clarity", "Analytics (only with consent)", "Measure how visitors use the site, including page views, clicks and scrolling, so we can improve it.", "Up to 12 months"),
    ]
    table = "".join(f"<tr><td>{e(a)}</td><td>{e(b)}</td><td>{e(c)}</td><td>{e(d)}</td><td>{e(x)}</td></tr>" for a, b, c, d, x in rows)
    body = hero(p, "about-river.jpg", "<h1>Cookie Policy</h1>") + f'''
    <section class="section"><div class="wrap legal">
      <p class="lead">This policy explains how Britcom Trading Limited, trading as Guilgal International ("we"), uses cookies and similar technologies on {SITE}.</p>
      <h2>What cookies are</h2>
      <p>Cookies are small files stored on your device by websites you visit. Some are essential for a site to work; others help the site owner understand how it is used.</p>
      <h2>Cookies we use</h2>
      <div class="table-scroll"><table class="dtable"><thead><tr><th>Name</th><th>Set by</th><th>Type</th><th>Purpose</th><th>Duration</th></tr></thead><tbody>{table}</tbody></table></div>
      <h2>Analytics</h2>
      <p>We use Microsoft Clarity to understand how visitors use our public pages. Clarity records interactions such as clicks, scrolling and mouse movement and produces heatmaps and session replays; text you type into forms is masked. Clarity cookies are set only if you choose "Accept analytics". Clarity is never used on the private partner portal, the partner login or the admin pages. Microsoft's privacy statement: <a href="https://privacy.microsoft.com/privacystatement">privacy.microsoft.com</a>.</p>
      <h2>Hosting</h2>
      <p>The site is hosted by Netlify. Netlify processes technical data such as IP addresses to deliver the site and protect it from abuse; it does not set analytics or advertising cookies on this site. Enquiry forms are processed through Netlify Forms.</p>
      <h2>Changing your choice</h2>
      <p>You can change your choice at any time using <a href="#" data-cookie-settings>Cookie settings</a> (also in the footer of every page), or by clearing cookies in your browser.</p>
      <h2>Contact</h2>
      <p>Questions about this policy: <a href="mailto:{EMAIL}">{EMAIL}</a>. {LEGAL}</p>
      <p class="small">Last updated {date.today().strftime("%-d %B %Y")}.</p>
    </div></section>
'''
    page("cookies/", "Cookie Policy | Guilgal International", "How Guilgal International uses cookies.", "", body, p)


def seo():
    pub = ["", "about/", "about/team/", "investors/", "contact/", "privacy/", "cookies/", "terms/"]
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
                                      "".join(f"  <url><loc>{SITE}/{u}</loc></url>\n" for u in pub) + "</urlset>\n")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nDisallow: /members/\nDisallow: /admin/\nDisallow: /login/\nDisallow: /archive/\n\nSitemap: {SITE}/sitemap.xml\n")


def qr_name(slug):
    return "p" + hashlib.sha256((QR_SALT + slug).encode()).hexdigest()[:16]


def private_media():
    """Point private pages at members/media/ for project-only images, write the QR codes
    under hashed names and a private manifest the admin panel reads after sign-in."""
    media = ROOT / MEDIA
    names = {f.name for f in media.iterdir() if f.is_file()}
    for f in (ROOT / "members").rglob("*.html"):
        h = f.read_text()
        h2 = re.sub(r"public/images/v2/([\w.-]+)", lambda m: (MEDIA + m.group(1)) if m.group(1) in names else m.group(0), h)
        if h2 != h:
            f.write_text(h2)
    qr("login/", "login")
    manifest = {}
    for slug, name, _ in PROJECTS:
        code = qr(f"members/projects/{slug}/", qr_name(slug))
        manifest[slug] = {"name": name, "qr": code[:-4], "url": f"{SITE}/members/projects/{slug}/"}
    (media / "projects.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    # news() is paused for now; /news/ redirects home (netlify.toml)
    home(); about(); team(); investors(); contact(); members(); login(); admin(); thanks()
    for s, n, _ in PROJECTS:
        project_page(s, n)
        brief_page(s, n)
    for s, t in [("privacy", "Privacy Policy"), ("terms", "Terms of Use")]:
        legal(s, t)
    cookie_policy()
    seo()
    private_media()
    if shutil.which("node"):
        subprocess.run(["node", str(ROOT / "tools" / "briefs.mjs")], check=True)
    else:
        print("node not found: project brief PDFs were not regenerated (run node tools/briefs.mjs)")
    print("built")
