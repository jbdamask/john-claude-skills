# Nano Banana API Reference

## Models

| Model | ID | Best For |
|-------|-----|----------|
| Nano Banana | `gemini-2.5-flash-image` | Speed, batch processing, previews |
| Nano Banana Pro | `gemini-3-pro-image-preview` | Professional assets, text in images, 4K output |

## Setup

```bash
pip install google-genai Pillow
```

API key from https://aistudio.google.com/apikey. Set as `GOOGLE_API_KEY` or `GEMINI_API_KEY` env var, or pass directly:

```python
from google import genai
client = genai.Client(api_key="YOUR_KEY")
```

## Text-to-Image

```python
from google import genai
from google.genai import types

client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents="A watercolor painting of a mountain lake at sunrise",
)

for part in response.parts:
    if part.text is not None:
        print(part.text)
    elif part.inline_data is not None:
        part.as_image().save("output.png")
```

## Image Editing (Image + Text Input)

```python
from PIL import Image

response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=["Make the sky more dramatic", Image.open("photo.png")],
)
```

## Pro Model with Config

```python
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents="A product mockup for a coffee brand called Nebula Brew",
    config=types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        image_config=types.ImageConfig(
            aspect_ratio="16:9",
            image_size="2K",
        ),
    ),
)
```

## Multi-Turn Chat

```python
chat = client.chats.create(
    model="gemini-3-pro-image-preview",
    config=types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
    ),
)

response = chat.send_message("Create a logo for a space-themed cafe")
# ... save image ...

response = chat.send_message("Now make it more minimalist and change colors to blue tones")
# ... save updated image ...
```

## Multiple Reference Images

Up to 14 reference images (6 objects max, 5 humans max):

```python
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=[
        "Create a group photo of these people at a beach",
        Image.open("person1.png"),
        Image.open("person2.png"),
        Image.open("person3.png"),
    ],
    config=types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        image_config=types.ImageConfig(aspect_ratio="16:9", image_size="2K"),
    ),
)
```

## Google Search Grounding (Pro Only)

```python
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents="Create an infographic of today's weather in Tokyo",
    config=types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        tools=[{"google_search": {}}],
    ),
)
```

## Supported Parameters

### Aspect Ratios
`1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`

### Resolutions (Pro Only)
`1K`, `2K`, `4K` (uppercase K required)

### Response Modalities
`["TEXT", "IMAGE"]` — include both to get text explanation alongside the image.

## Response Handling

```python
for part in response.parts:
    if part.text is not None:
        print(part.text)
    elif part.inline_data is not None:
        image = part.as_image()  # Returns PIL Image
        image.save("output.png")
```

## Constraints

- All generated images include SynthID watermark
- Batch API available for high-volume (24-hour turnaround)
- Image-based search results excluded when using Google Search grounding
- Preserve thought signatures across multi-turn conversations
- Subject to Google's Prohibited Use Policy
