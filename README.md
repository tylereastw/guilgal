# GUILGAL — website

Premium corporate editorial homepage for GUILGAL, built to the design brief and the two
supplied reference designs. Static HTML/CSS/JS — open `index.html`, no build step.

## Structure
Three sections, matching the reference designs:

| # | Section | Layout |
|---|---|---|
| 1 | Hero — *Resources for a Stronger DRC* | text left; gold-outlined DRC map filled with landscape; outcrop overlapping bottom-left; contour lines; curved gold-edged transition |
| 2 | Our Focus — *Sustainable Development, Real Impact* | ivory; three overlapping angled photo panels; quote beneath |
| 3 | Our Approach — *From exploration to discovery* | dark panoramic photo; text right; contour lines flowing into the footer |

Navigation links other than "Our Approach" point to `#` until those pages exist.

## Photography
The supplied artwork lives in `public/images/`:

| File | Position |
|---|---|
| `guilgal_hero_background_1920x1080.png` | hero background |
| `guilgal_drc_map_layer.png` | DRC silhouette overlay in the hero (transparent PNG with gold outline) |
| `guilgal_focus_triptych.png` | Our Focus angled triptych (transparent PNG) |
| `guilgal_approach_natural_mirrored.png` | Our Approach background |

## Fonts
DM Serif Display (regular, italic) and DM Sans (variable 400–700, regular and italic) are
self-hosted as WOFF2 in `assets/fonts/` and declared in `css/fonts.css`. There are no requests
to Google Fonts or any other third party; the page makes no external requests at all.
Both families are licensed under the SIL Open Font License.

## Placeholders to replace
- Navigation links (About, Expertise, Minerals, Investors, Contact, Discuss an Opportunity) — point to their pages once built.
