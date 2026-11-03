# Licensed webfonts go here

The site is set up for **Canela** (headings) and **Neue Haas Grotesk Text** (body, navigation, UI).
Both need a web licence before they can be self-hosted. Add these WOFF2 files:

| File | Typeface | Use |
|---|---|---|
| `Canela-Regular-Web.woff2` | Canela Regular | hero, section and supporting headings |
| `Canela-RegularItalic-Web.woff2` | Canela Regular Italic | italic emphasis, large numerals (01–04) |
| `NHaasGroteskTXPro-55Rg.woff2` | Neue Haas Grotesk Text 55 Roman | body copy |
| `NHaasGroteskTXPro-56It.woff2` | Neue Haas Grotesk Text 56 Italic | occasional italic in body |
| `NHaasGroteskTXPro-65Md.woff2` | Neue Haas Grotesk Text 65 Medium | navigation, buttons, labels, dates |

Sources: Canela from Commercial Type (commercialtype.com); Neue Haas Grotesk from Monotype/Linotype
(monotype.com). If the files you receive have different names, update the `url()` paths in
`css/fonts.css`. Until the files are present the site uses its current fallback pair
(DM Serif Display / DM Sans).
