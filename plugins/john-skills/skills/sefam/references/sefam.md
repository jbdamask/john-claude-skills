# Style: sefam (signature)

**Feel:** Maximalist, joyful anime/manga poster — Saturday-morning cartoon energy meets Shibuya street art. Exuberant, optimistic, hand-crafted, never corporate or minimal. This is the skill's signature look.

**Best for:** a celebratory or high-energy explainer for an internal/friendly audience — a launch, a win, a fun internal update. Not a somber post-mortem or an external board deck.

**Build prompt:**

**Palette** — saturated primaries and candy tones, everything at full saturation, no muted or pastel colors: cobalt blue (`#1f4fd8`), sunburst yellow (`#ffcf1a`), hot pink (`#ff3fa4`), teal (`#12c2c2`), tangerine orange (`#ff7a1a`), violet purple (`#8a3ffb`).

**Background** (layer these):
- Radial sunburst rays emanating from center in alternating warm colors (yellow / orange / pink), over a cobalt sky. Build with a `repeating-conic-gradient` for the rays.
- Stylized puffy white clouds and rainbow arcs.
- Halftone dot texture (CSS `radial-gradient` dot pattern) and scattered star shapes — four-point sparkles and five-point stars — in white, gold, and pink.

**Typography:**
- Headings / hero title: huge, bouncy bubble letters. Each letter can be a different color (yellow, pink, teal, orange, purple), with thick dark-navy outlines (`-webkit-text-stroke` or layered `text-shadow`), glossy white highlight streaks, and a hard (no-blur) drop shadow. Slight per-letter rotation for a hand-lettered feel. Chunky rounded display feel — use a system fallback stack that reads chunky/rounded (no webfonts; the Artifact CSP blocks them), e.g. `"Arial Rounded MT Bold", "Comic Sans MS", system-ui, sans-serif`, heavy weight.
- Emphasis text can sit in white rounded "sticker" pills, with multicolored words and small dashes / tick marks flanking it.

**UI treatment** — everything is a sticker:
- Cards and buttons: white or bright fills, thick dark outlines (`3–4px solid #10204a`), big `border-radius`, offset SOLID drop shadows (no blur, e.g. `box-shadow: 8px 8px 0 #10204a`). Slight alternating tilt on cards.
- Springy, squash/bounce hover states.

**Motion** (JS only for small animations):
- Gentle floating / bobbing on stars and clouds, subtle slow rotation on the sunburst rays, springy hover states. Lively but not seizure-inducing — slow durations, small amplitudes. Respect `prefers-reduced-motion` by disabling the loops.

**Accents:** comic-book exclamation marks, speed lines, and confetti-like sparkles in section dividers.

**Readability is non-negotiable:** the background is busy, so all copy lives inside white sticker/pill containers with strong contrast. Body text stays ~1.1rem and genuinely readable. Light, high-saturation design — do not force theme-switching.
