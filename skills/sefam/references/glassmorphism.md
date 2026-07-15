# Style: Glassmorphism

**Feel:** Apple-inspired translucent depth — frosted cards, soft color, clean and premium.

**Best for:** a modern product or UI-facing explainer; something that should feel current and polished.

**Build prompt:**
- Soft colorful blurred background — a gentle multi-color gradient (e.g. `#6a8dff` → `#c86dd7` → `#ffd6a5`), lightly blurred.
- Frosted translucent cards: `background: rgba(255,255,255,0.15); backdrop-filter: blur(16px);` with thin light borders (`1px solid rgba(255,255,255,0.3)`).
- Layered depth — cards float above the background; use soft, diffuse shadows.
- Rounded corners (`border-radius: 16–20px`).
- Modern system-sans: `-apple-system, "SF Pro Text", system-ui, sans-serif`.
- Watch contrast — translucent panels can wash out text. Darken the card or text enough that body copy (~1.1rem) stays clearly readable.
- Can lean light or dark; pick one and commit. Do not force theme-switching.
