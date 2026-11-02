# GUILGAL — homepage: "From the canopy to the seam"

Static HTML/CSS/JS, no build step — open `index.html` in a browser.

The page is one descent. Photos are treated as prints laid over each other; every layer
moves at its own speed, so they slide across one another as you scroll.

| # | Chapter | What you see |
|---|---|---|
| 00 | Above the canopy | Full-bleed sunrise; a print of the ore lies over its corner — the end of the story shown at the start |
| 01 | The archive | Our Approach copy beside a desk of sepia prints (aerial survey, field book, map sheet) |
| 02 | The field | Pinned: four prints land on top of each other as you scroll, the background turns from forest to earth, a depth counter runs 0 → 120 m, the four steps light in turn |
| 03 | The seam | Ore photo full-bleed; the six commodities set as giant type across it |
| 04 | The record | Wide landscape with the 10+ / 10+ / 100% block overlapping its edge, hand-sample print on top |
| 05 | Back to the surface | Sunrise returns; call to action, John Paul Boardman's details, tilted paper form |

A gold survey line on the left (desktop) fills as you descend, with a readout of where you are.

## Photo slots
Every image is a `.ph` element with a `data-slot` label. Drop a file with that name into
`assets/img/` and update the `src`. Current files are low-resolution crops of the mockup —
replace them all for production.

| Slot | Chapter |
|---|---|
| hero-landscape.jpg, ore-detail.jpg | 00 |
| archive-aerial.jpg, archive-river.jpg, archive-map.jpg | 01 (shown sepia) |
| field-canopy.jpg, field-sampling.jpg, field-drilling.jpg, field-core.jpg | 02 |
| ore-wide.jpg | 03 |
| record-landscape.jpg, record-sample.jpg | 04 |
| sky-sun.jpg | 05 |

## Still to fill in
- Telephone, e-mail, address (shown as —)
- Form handler (`TODO` in `js/main.js`)
- Captions on the prints ("Aerial survey · 1978", "Day 19 · Hole GG-03"…) are placeholders to replace with real ones
