# GUILGAL — website

Premium corporate editorial homepage for GUILGAL, built to the design brief and the two
supplied reference designs. Static HTML/CSS/JS — open `index.html`, no build step.

## Structure
| # | Section | Surface | Layout |
|---|---|---|---|
| 1 | Hero — *Resources for a Stronger DRC* | dark teal photo | text left, gold-outlined DRC map filled with landscape, outcrop overlapping bottom-left, contour lines, curved gold-edged transition |
| 2 | Our Focus — *Sustainable Development, Real Impact* | ivory | three overlapping angled photo panels, quote beneath |
| 3 | Our Approach — *From exploration to discovery* | dark panoramic photo | text right, contour lines flowing out |
| 4 | Geological Expertise | ivory, text-led | two-column editorial with four-line programme list |
| 5 | Mineral Portfolio | charcoal | mineral photo fading in from the left, six commodities |
| 6 | Exploration & Development process | ivory, minimal | four numbered steps |
| 7 | The DRC's potential | full-width photo | light-to-dark gradient entry, facts row |
| 8 | Responsible Development | ivory | text + arched photo |
| 9 | Investors | charcoal | text + fact list, gold CTA |
| 10 | The Company | ivory | two-column copy |
| 11 | Contact | dark photo | details + underlined form |

Each section edge is a different curve; no two transitions repeat.

## Adding the photography
Every image slot shows a dashed label until its file exists. Put the file in `assets/img/`
with the exact name below and it appears — no code changes needed.

| File | Position | Size (px) | Subject |
|---|---|---|---|
| `hero.jpg` | 1 · hero background | 2400 × 1400 | DRC landscape at sunset, dark teal tones, river valley |
| `map-fill.jpg` | 1 · inside the DRC outline | 1200 × 1200 | river valley, forest and sunset (square crop, centre of interest in the middle) |
| `outcrop.jpg` | 1 · bottom-left overlap | 1200 × 600 | rocky outcrop, lit from the right; edges are faded in CSS |
| `focus-mine.jpg` | 2 · first panel | 900 × 1200 | open-pit mine / haul road |
| `focus-forest.jpg` | 2 · second panel, and 8 · arched photo | 900 × 1200 | lush green DRC countryside |
| `focus-mountain.jpg` | 2 · third panel | 900 × 1200 | mountainous landscape |
| `approach-hills.jpg` | 3 · background, and 11 · contact background | 2400 × 1100 | misty panoramic hills, dark green |
| `minerals.jpg` | 5 · left half | 1400 × 1600 | mineral / ore close-up |
| `drc-panorama.jpg` | 7 · background | 2400 × 1000 | wide DRC terrain |

For a different phone crop of the hero, add `hero-mobile.jpg` (1200 × 1800) and switch the
`<img>` in the hero to a `<picture>` with a `(max-width: 760px)` source.

## Fonts
DM Serif Display (regular, italic) and DM Sans (variable 400–700, regular and italic) are
self-hosted as WOFF2 in `assets/fonts/` and declared in `css/fonts.css`. There are no requests
to Google Fonts or any other third party; the page makes no external requests at all.
Both families are licensed under the SIL Open Font License.

## Placeholders to replace
- Contact telephone, e-mail and address (shown as —).
- `[Verified figure]` / `[Verified information]` in sections 7 and 9 — no statistics or licence
  claims have been invented.
- Form submission handler (`TODO` in `js/main.js`).
- The DRC outline is traced from approximate border coordinates; swap in an official vector if required.
