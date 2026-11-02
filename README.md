# GUILGAL — website redesign

A single-page, scroll-driven "journey" for guilgal.org. Static HTML/CSS/JS, no build step — open `index.html` in a browser.

## The story, chapter by chapter
| | Chapter | What happens on scroll |
|---|---|---|
| — | **Arrival** (hero) | Sunrise over the Congo basin; the rainforest canopy parallaxes away as you scroll. |
| — | **Prologue** | The sentence lights up word by word as you read. |
| 01 | **The Archive** | A historic contour survey sheet draws itself, then sample targets ping. |
| 02 | **The Field** | Pinned scene: a drill hole descends through topsoil → laterite → saprolite → copper oxide zone → primary ore, with a live depth counter, samples logged and the four steps (reconnaissance → sampling → drilling → evidence) advancing. |
| 03 | **The Discovery** | Malachite close-up with the six commodities as element tiles. |
| 04 | **The Record** | 10+ / 10+ / 100% count up; DRC → London / Australia route map. |
| 05 | **Your Project** | Back to the sunrise — contact details and form. |

A journey rail on the left (desktop) tracks progress and shows a position readout (altitude, then drill depth).

## Files
- `index.html` — markup and copy
- `css/styles.css` — design tokens at the top (`--gold`, `--night`, `--paper`…)
- `js/main.js` — scroll scenes, generated scenery (canopy, ridges, contours), counters, form validation
- `assets/img/` — imagery cropped from the design mockup (replace with high-resolution originals for production)

## Before going live
- Fill in the real telephone, e-mail and address in the contact card (placeholders now).
- Connect the form to a handler (see `TODO` in `js/main.js`).
- Swap `assets/img/*.jpg` for full-resolution photography.
