import os
import re
import base64
import pathlib
import requests
from dotenv import load_dotenv

load_dotenv()


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def generate_thumbnail(topic: str, slug: str) -> str | None:
    """
    Generate a cybersecurity-themed thumbnail using Together AI (FLUX.1-schnell-Free).
    Falls back to Hugging Face if Together AI fails.
    Returns the local file path to the saved PNG, or None on failure.
    """
    pathlib.Path("outputs").mkdir(exist_ok=True)
    output_path = str(pathlib.Path("outputs") / f"{slug}_thumbnail.png")

    prompt = (
        f"Cybersecurity themed professional blog thumbnail for: {topic}. "
        "Dark background, neon blue and green accents, digital network patterns, "
        "shield icons, futuristic style, high quality, no text."
    )

    # Primary: Together AI
    together_key = os.getenv("TOGETHER_API_KEY")
    if together_key:
        try:
            import together
            together.api_key = together_key
            response = together.Images.create(
                prompt=prompt,
                model="black-forest-labs/FLUX.1-schnell-Free",
                width=1024,
                height=576,
                steps=4,
                n=1,
            )
            # Handle both URL and base64 response formats
            img_data = response.data[0]
            if hasattr(img_data, "b64_json") and img_data.b64_json:
                with open(output_path, "wb") as f:
                    f.write(base64.b64decode(img_data.b64_json))
                return output_path
            elif hasattr(img_data, "url") and img_data.url:
                img_bytes = requests.get(img_data.url, timeout=30).content
                with open(output_path, "wb") as f:
                    f.write(img_bytes)
                return output_path
        except Exception as e:
            print(f"Together AI image generation failed: {e}. Trying fallback...")

    # Fallback: Hugging Face Inference API
    hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
    if hf_token:
        try:
            api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
            headers = {"Authorization": f"Bearer {hf_token}"}
            response = requests.post(api_url, headers=headers, json={"inputs": prompt}, timeout=60)
            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return output_path
        except Exception as e:
            print(f"Hugging Face image generation failed: {e}")

    return None
