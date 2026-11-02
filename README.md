# GUILGAL — homepage

Static HTML/CSS/JS built to the approved mockup — open `index.html` in a browser, no build step.

Page flow (each band is cut on a diagonal with a gold edge, so scrolling reads as one continuous journey):

1. **Hero** — full-bleed landscape, headline with gold bar, *Discover More*
2. **Our Approach** — malachite photo left, cream paper panel right
3. **Stats** — 10+ / 10+ / 100% over a landscape photo, gold corner
4. **Our Services / Key Strengths** — mirrored: paper panel left, field photo right
5. **Opportunities** — copper, lithium, tantalum, tin, niobium, wolframite over a photo
6. **Contact** — call to action and John Paul Boardman on the landscape, form on a paper panel

## Photo slots
Drop files with these names into `assets/img/` — each replaces its labelled placeholder automatically.

| File | Used for | Suggested size |
|---|---|---|
| `hero-landscape.jpg` | Hero + contact background (currently a low-res crop of the mockup) | 2400×1400 |
| `malachite.jpg` | Our Approach (currently a low-res crop of the mockup) | 1800×1400 |
| `landscape-hills.jpg` | Stats band | 2400×900 |
| `field-team.jpg` | Our Services | 1800×1400 |
| `core-samples.jpg` | Opportunities band | 2400×1000 |

## Still to fill in
- Telephone, e-mail and address in the contact block (shown as —)
- Form handler (`TODO` in `js/main.js`)
