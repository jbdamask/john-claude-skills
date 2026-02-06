#!/usr/bin/env python3
"""
Generate images using Google's Nano Banana API (Gemini image models).

Usage:
    python generate_image.py --prompt "A sunset over mountains" [options]

Options:
    --prompt TEXT        Image generation prompt (required)
    --model MODEL        Model ID: "flash" for gemini-2.5-flash-image,
                         "pro" for gemini-3-pro-image-preview (default: flash)
    --output PATH        Output file path (default: generated_image.png)
    --aspect-ratio RATIO Aspect ratio (default: 1:1)
                         Options: 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9
    --resolution RES     Resolution: 1K, 2K, 4K (default: 1K, Pro model only)
    --search             Enable Google Search grounding (Pro model only)
    --input-image PATH   Input image for editing (optional, can specify multiple)

Requires:
    pip install google-genai Pillow

Environment:
    GOOGLE_API_KEY or GEMINI_API_KEY must be set
"""

import argparse
import os
import sys

# Auto-detect venv when present
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
VENV_SITE = os.path.join(SKILL_DIR, ".venv", "lib")
if os.path.isdir(VENV_SITE):
    import glob
    matches = glob.glob(os.path.join(VENV_SITE, "python*", "site-packages"))
    if matches:
        sys.path.insert(0, matches[0])

def get_api_key():
    key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not key:
        print("Error: Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable.", file=sys.stderr)
        print("Get a key at: https://aistudio.google.com/apikey", file=sys.stderr)
        sys.exit(1)
    return key

def main():
    parser = argparse.ArgumentParser(description="Generate images with Nano Banana API")
    parser.add_argument("--prompt", required=True, help="Image generation prompt")
    parser.add_argument("--model", default="flash", choices=["flash", "pro"],
                        help="Model: flash (fast) or pro (high quality)")
    parser.add_argument("--output", default="generated_image.png", help="Output file path")
    parser.add_argument("--aspect-ratio", default="1:1",
                        choices=["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"])
    parser.add_argument("--resolution", default=None, choices=["1K", "2K", "4K"],
                        help="Output resolution (Pro model only)")
    parser.add_argument("--search", action="store_true", help="Enable Google Search grounding (Pro only)")
    parser.add_argument("--input-image", action="append", dest="input_images",
                        help="Path to input image for editing (can specify multiple)")
    args = parser.parse_args()

    model_ids = {
        "flash": "gemini-2.5-flash-image",
        "pro": "gemini-3-pro-image-preview",
    }
    model_id = model_ids[args.model]

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("Error: google-genai package not installed. Run: pip install google-genai", file=sys.stderr)
        sys.exit(1)

    api_key = get_api_key()
    client = genai.Client(api_key=api_key)

    # Build contents
    contents = []
    if args.input_images:
        from PIL import Image
        contents.append(args.prompt)
        for img_path in args.input_images:
            if not os.path.exists(img_path):
                print(f"Error: Image not found: {img_path}", file=sys.stderr)
                sys.exit(1)
            contents.append(Image.open(img_path))
    else:
        contents = args.prompt

    # Build config
    config_kwargs = {"response_modalities": ["TEXT", "IMAGE"]}
    image_config_kwargs = {"aspect_ratio": args.aspect_ratio}

    if args.resolution and args.model == "pro":
        image_config_kwargs["image_size"] = args.resolution

    config_kwargs["image_config"] = types.ImageConfig(**image_config_kwargs)

    if args.search and args.model == "pro":
        config_kwargs["tools"] = [{"google_search": {}}]

    config = types.GenerateContentConfig(**config_kwargs)

    print(f"Generating image with {model_id}...")
    response = client.models.generate_content(
        model=model_id,
        contents=contents,
        config=config,
    )

    image_saved = False
    for part in response.parts:
        if part.text is not None:
            print(f"Model response: {part.text}")
        elif part.inline_data is not None:
            image = part.as_image()
            image.save(args.output)
            print(f"Image saved to: {args.output}")
            image_saved = True

    if not image_saved:
        print("Warning: No image was generated. The model may have declined the request.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
