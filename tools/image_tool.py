import os
import re
import base64
import pathlib
import requests
from dotenv import load_dotenv

load_dotenv()


def generate_thumbnail(topic: str, slug: str) -> str | None:
    """
    Generate a cybersecurity-themed thumbnail.
    Tries in order: Together AI → Hugging Face (free).
    Returns local file path or None on failure.
    """
    pathlib.Path("outputs").mkdir(exist_ok=True)
    output_path = str(pathlib.Path("outputs") / f"{slug}_thumbnail.png")

    prompt = (
        f"Cybersecurity professional blog thumbnail, topic: {topic}. "
        "Dark background, neon blue and green accents, digital network patterns, "
        "shield and lock icons, futuristic style, high quality, no text, no watermark."
    )

    # Option 1: Together AI (requires credits at api.together.ai)
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
                with open(output_path, "wb") as f:
                    f.write(base64.b64decode(img_data.b64_json))
                return output_path
            elif hasattr(img_data, "url") and img_data.url:
                img_bytes = requests.get(img_data.url, timeout=30).content
                with open(output_path, "wb") as f:
                    f.write(img_bytes)
                return output_path
        except Exception as e:
            print(f"Together AI failed: {e}. Trying Hugging Face...")

    # Option 2: Hugging Face Inference API (free with HF token)
    hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
    headers = {"Authorization": f"Bearer {hf_token}"} if hf_token else {}
    hf_models = [
        "stabilityai/stable-diffusion-xl-base-1.0",
        "runwayml/stable-diffusion-v1-5",
    ]
    for model in hf_models:
        try:
            url = f"https://api-inference.huggingface.co/models/{model}"
            response = requests.post(
                url, headers=headers,
                json={"inputs": prompt},
                timeout=90,
            )
            if response.status_code == 200 and "image" in response.headers.get("content-type", ""):
                with open(output_path, "wb") as f:
                    f.write(response.content)
                print(f"Thumbnail generated via {model}")
                return output_path
        except Exception as e:
            print(f"HuggingFace {model} failed: {e}")

    print("All thumbnail providers failed. Add HUGGINGFACE_API_TOKEN to .env for free image generation.")
    return None
