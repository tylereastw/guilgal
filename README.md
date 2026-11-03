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
No separate photo files were supplied, so the images in `assets/img/` are cut from the two
approved reference mockups (desktop and mobile) and should be replaced with the original
full-resolution photographs when available — same file names, no code changes:

| File | Position | Notes |
|---|---|---|
| `hero.jpg` | hero background | composed from the mockup's misty hills + outcrop; sunset glow top-right |
| `map-fill.jpg` | inside the DRC outline | sunset river valley from the mockup map |
| `focus-mine.jpg`, `focus-forest.jpg`, `focus-mountain.jpg` | the three angled panels | exact panel crops; the clip-path matches the mockup's slant |
| `approach-hills.jpg` | Our Approach background | mockup panorama, mirrored |

The DRC outline is the real boundary (from a public-domain country GeoJSON), scaled uniformly.

## Fonts
DM Serif Display (regular, italic) and DM Sans (variable 400–700, regular and italic) are
self-hosted as WOFF2 in `assets/fonts/` and declared in `css/fonts.css`. There are no requests
to Google Fonts or any other third party; the page makes no external requests at all.
Both families are licensed under the SIL Open Font License.

## Placeholders to replace
- Navigation links (About, Expertise, Minerals, Investors, Contact, Discuss an Opportunity) — point to their pages once built.
