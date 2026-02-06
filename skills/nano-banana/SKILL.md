---
name: nano-banana
description: "Generate and edit images using Google's Nano Banana API (Gemini image models). Use when the user asks to generate images, create AI art, edit photos, do text-to-image, image-to-image editing, or any task involving Nano Banana, Nano Banana Pro, or Gemini image generation. Triggers on: generate image, create image, nano banana, image generation, AI image, edit photo with AI, text to image."
---

# Nano Banana Image Generation

Generate and edit images via Google's Nano Banana API using the `google-genai` Python SDK.

## Setup (one-time)

```bash
./scripts/setup.sh
```

Creates `.venv` and installs `google-genai` and `Pillow`. Scripts auto-detect the venv when present.

Set `GOOGLE_API_KEY` or `GEMINI_API_KEY` env var. Get a key at https://aistudio.google.com/apikey.

## Model Selection

- **Nano Banana** (`gemini-2.5-flash-image`) — Fast, cheap. Use for quick previews, batch jobs, simple generation.
- **Nano Banana Pro** (`gemini-3-pro-image-preview`) — High quality, up to 4K, accurate text rendering, multi-reference images, Google Search grounding. Use for professional assets, text-heavy images, complex prompts.

## Quick Start

### Generate an image

```python
from google import genai
from google.genai import types

client = genai.Client()
response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents="A watercolor painting of a mountain lake at sunrise",
)
for part in response.parts:
    if part.inline_data is not None:
        part.as_image().save("output.png")
```

### Edit an existing image

```python
from PIL import Image

response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=["Make the sky more dramatic", Image.open("photo.png")],
)
```

### Pro model with resolution and aspect ratio

```python
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents="A product mockup for a coffee brand",
    config=types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        image_config=types.ImageConfig(aspect_ratio="16:9", image_size="2K"),
    ),
)
```

## Helper Script

Run `scripts/generate_image.py` for CLI-based generation:

```bash
python scripts/generate_image.py --prompt "A sunset over mountains" --model flash --output sunset.png
python scripts/generate_image.py --prompt "Product packaging" --model pro --resolution 4K --aspect-ratio 3:2
python scripts/generate_image.py --prompt "Edit the background" --model flash --input-image photo.png
```

## Key Parameters

- **Aspect ratios**: `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`
- **Resolutions** (Pro only): `1K`, `2K`, `4K` (uppercase K required)
- **Reference images** (Pro only): Up to 14 total (6 objects max, 5 humans max)
- **Google Search grounding** (Pro only): `tools=[{"google_search": {}}]`

## Advanced Usage

For multi-turn chat, multiple reference images, and detailed API parameters, see [references/api_reference.md](references/api_reference.md).

## Prompting Tips

- Describe scenes narratively rather than listing keywords
- Specify style, lighting, and composition for better results
- For text in images, use Nano Banana Pro — it handles legible text rendering

## Constraints

- All generated images include a SynthID watermark
- Preserve thought signatures across multi-turn conversations
- Subject to Google's Prohibited Use Policy
