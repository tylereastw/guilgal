# GUILGAL — website

Premium corporate editorial homepage for GUILGAL, built to the design brief and the two
supplied reference designs. Static HTML/CSS/JS — open `index.html`, no build step.

## Structure
Five sections:

| # | Section | Layout |
|---|---|---|
| 1 | Hero — *Resources for a Stronger DRC* | text left; gold-outlined DRC map filled with landscape; outcrop overlapping bottom-left; contour lines; curved gold-edged transition |
| 2 | Our Focus — *Sustainable Development, Real Impact* | ivory; three overlapping angled photo panels; quote beneath |
| 3 | Our Approach — *Identify. Evaluate. Partner. Develop.* | ivory; lead with gold rule; four numbered steps joined by gold arrows |
| 4 | News & Milestones | ivory; three news cards (photo, date, title, arrow) and "View all updates" |
| 5 | Our Approach — *From exploration to discovery* | panorama anchored at its top so the pale sky blends out of the ivory; text right over the hills |

Navigation links other than "Our Approach" point to `#` until those pages exist.

## Photography
The supplied artwork lives in `public/images/`:

| File | Position |
|---|---|
| `guilgal_hero_background_1920x1080.png` | hero background |
| `guilgal_drc_map_layer.png` | DRC silhouette overlay in the hero (transparent PNG with gold outline) |
| `guilgal_focus_triptych.png` | Our Focus angled triptych (transparent PNG) |
| `guilgal_approach_natural_mirrored.png` | Our Approach panorama background |
| `news-1.jpg`, `news-2.jpg`, `news-3.jpg` | news card photos (crops of the supplied artwork; replace with each post's own image, e.g. the drilling rig for the third) |

## Fonts
Specified pairing: **Canela** (headings; Regular and Italic) and **Neue Haas Grotesk Text**
(body Regular; navigation, buttons and labels Medium). Both are commercial typefaces that need a
web licence, so they are **not included yet**. `css/fonts.css` declares them, and they load
automatically once the WOFF2 files are placed in `assets/fonts/licensed/` (file names listed in
the README there). Until then the site falls back to the self-hosted DM Serif Display / DM Sans
pair (SIL Open Font License). No fonts are loaded from third parties.

## Placeholders to replace
- News cards: dates and titles are taken from the mock-up; link them to the real posts once the news pages exist.
- Navigation links (About, Expertise, Minerals, Investors, Contact, Discuss an Opportunity) — point to their pages once built.
