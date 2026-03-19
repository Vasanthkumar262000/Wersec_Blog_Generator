import os
import base64
import pathlib
import requests
from dotenv import load_dotenv

load_dotenv()


def _build_prompt(topic: str) -> str:
    return (
        f"Professional LinkedIn banner image for a cybersecurity company called Wersec. "
        f"Topic: {topic}. "
        "Visual style: dark background (#09090b), glowing neon blue and electric teal accents, "
        "subtle digital circuit board or neural network patterns in the background, "
        "a prominent metallic shield with a padlock icon in the foreground, "
        "clean corporate aesthetic suitable for a B2B security firm, "
        "cinematic depth of field, 4K quality, no text, no watermarks, no people, photorealistic."
    )


def _save(data: bytes, path: str) -> str:
    with open(path, "wb") as f:
        f.write(data)
    return path


def generate_thumbnail(topic: str, slug: str) -> str | None:
    """
    Generate a Wersec-branded cybersecurity thumbnail for LinkedIn.
    Provider priority: Google Imagen 4 → Together AI → Hugging Face.
    Returns local file path or None on failure.
    """
    pathlib.Path("outputs").mkdir(exist_ok=True)
    output_path = str(pathlib.Path("outputs") / f"{slug}_thumbnail.png")
    prompt = _build_prompt(topic)

    # ── Option 1: Google Imagen 4 (primary) ──────────────────────────────────
    google_key = os.getenv("GOOGLE_API_KEY")
    if google_key:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=google_key)
            response = client.models.generate_images(
                model="imagen-4.0-generate-001",
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio="16:9",        # ideal for LinkedIn posts
                    safety_filter_level="block_some",
                    person_generation="dont_allow",
                ),
            )
            image_bytes = response.generated_images[0].image.image_bytes
            print("Thumbnail generated via Google Imagen 4.")
            return _save(image_bytes, output_path)
        except Exception as e:
            print(f"Google Imagen 4 failed: {e}. Trying Together AI...")

    # ── Option 2: Together AI ─────────────────────────────────────────────────
    together_key = os.getenv("TOGETHER_API_KEY")
    if together_key:
        try:
            from together import Together
            client = Together(api_key=together_key)
            response = client.images.generate(
                prompt=prompt,
                model="black-forest-labs/FLUX.1-schnell-Free",
                width=1024,
                height=576,
                steps=4,
                n=1,
            )
            img_data = response.data[0]
            if hasattr(img_data, "b64_json") and img_data.b64_json:
                return _save(base64.b64decode(img_data.b64_json), output_path)
            elif hasattr(img_data, "url") and img_data.url:
                return _save(requests.get(img_data.url, timeout=30).content, output_path)
        except Exception as e:
            print(f"Together AI failed: {e}. Trying Hugging Face...")

    # ── Option 3: Hugging Face (free fallback) ────────────────────────────────
    hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
    headers = {"Authorization": f"Bearer {hf_token}"} if hf_token else {}
    for model in ["stabilityai/stable-diffusion-xl-base-1.0", "runwayml/stable-diffusion-v1-5"]:
        try:
            resp = requests.post(
                f"https://api-inference.huggingface.co/models/{model}",
                headers=headers,
                json={"inputs": prompt},
                timeout=90,
            )
            if resp.status_code == 200 and "image" in resp.headers.get("content-type", ""):
                print(f"Thumbnail generated via {model}.")
                return _save(resp.content, output_path)
        except Exception as e:
            print(f"HuggingFace {model} failed: {e}")

    print("All thumbnail providers failed. Add GOOGLE_API_KEY to .env (Gemini API key) to enable Google Imagen 4.")
    return None
