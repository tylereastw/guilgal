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

## Adding the photography
Every image slot shows a dashed label until its file exists. Put the file in `assets/img/`
with the exact name below and it appears — no code changes needed.

| File | Position | Size (px) | Subject |
|---|---|---|---|
| `hero.jpg` | 1 · hero background | 2400 × 1400 | DRC landscape at sunset, dark teal tones, river valley |
| `map-fill.jpg` | 1 · inside the DRC outline | 1200 × 1200 | river valley, forest and sunset (square crop, centre of interest in the middle) |
| `outcrop.jpg` | 1 · bottom-left overlap | 1200 × 600 | rocky outcrop, lit from the right; edges are faded in CSS |
| `focus-mine.jpg` | 2 · first panel | 900 × 1200 | open-pit mine / haul road |
| `focus-forest.jpg` | 2 · second panel | 900 × 1200 | lush green DRC countryside |
| `focus-mountain.jpg` | 2 · third panel | 900 × 1200 | mountainous landscape |
| `approach-hills.jpg` | 3 · background | 2400 × 1100 | misty panoramic hills, dark green |

For a different phone crop of the hero, add `hero-mobile.jpg` (1200 × 1800) and switch the
`<img>` in the hero to a `<picture>` with a `(max-width: 760px)` source.

## Fonts
DM Serif Display (regular, italic) and DM Sans (variable 400–700, regular and italic) are
self-hosted as WOFF2 in `assets/fonts/` and declared in `css/fonts.css`. There are no requests
to Google Fonts or any other third party; the page makes no external requests at all.
Both families are licensed under the SIL Open Font License.

## Placeholders to replace
- Navigation links (About, Expertise, Minerals, Investors, Contact, Discuss an Opportunity) — point to their pages once built.
- The DRC outline is traced from approximate border coordinates; swap in an official vector if required.
