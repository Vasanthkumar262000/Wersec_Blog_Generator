import os
import requests
from dotenv import load_dotenv

load_dotenv()

LINKEDIN_API_URL = "https://api.linkedin.com/v2/ugcPosts"
_HEADERS_BASE = {
    "X-Restli-Protocol-Version": "2.0.0",
    "Content-Type": "application/json",
}


def _auth_headers(token: str) -> dict:
    return {**_HEADERS_BASE, "Authorization": f"Bearer {token}"}


def _upload_image(token: str, person_urn: str, image_path: str) -> str | None:
    """
    Upload a local image to LinkedIn and return the asset URN.
    LinkedIn requires a two-step process: register the upload, then PUT the bytes.
    """
    headers = _auth_headers(token)

    # Step 1 — register upload and get the upload URL + asset URN
    register_payload = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": person_urn,
            "serviceRelationships": [
                {
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent",
                }
            ],
        }
    }
    resp = requests.post(
        "https://api.linkedin.com/v2/assets?action=registerUpload",
        headers=headers,
        json=register_payload,
        timeout=30,
    )
    if resp.status_code != 200:
        print(f"LinkedIn image register failed: {resp.status_code} — {resp.text}")
        return None

    data = resp.json()
    try:
        asset_urn = data["value"]["asset"]
        upload_url = data["value"]["uploadMechanism"][
            "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
        ]["uploadUrl"]
    except KeyError as e:
        print(f"LinkedIn register response missing key: {e}")
        return None

    # Step 2 — upload the raw image bytes
    with open(image_path, "rb") as f:
        img_bytes = f.read()

    upload_resp = requests.put(
        upload_url,
        data=img_bytes,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "image/png",
        },
        timeout=60,
    )
    if upload_resp.status_code not in (200, 201):
        print(f"LinkedIn image upload failed: {upload_resp.status_code} — {upload_resp.text}")
        return None

    print(f"LinkedIn image uploaded. Asset: {asset_urn}")
    return asset_urn


def _format_linkedin_post(topic: str, full_content: str, summary: str) -> str:
    """Fallback plain-text formatter when no AI-optimised post is available."""
    hashtags = "\n\n#Cybersecurity #InfoSec #AI #Wersec"
    lines = full_content.split("\n")
    clean = []
    for line in lines:
        line = line.strip().lstrip("#").strip()
        if line and not line.startswith("```"):
            clean.append(line)
        if len("\n".join(clean)) > 1800:
            break
    post = f"{topic}\n\n{summary}\n\n" + "\n".join(clean[:20]) + hashtags
    return post[:3000]


def post_to_linkedin(
    topic: str,
    full_content: str,
    summary: str,
    linkedin_post: str = "",
    image_path: str | None = None,
) -> bool:
    """
    Post to LinkedIn as a text update (with optional image thumbnail).

    Setup:
      1. LinkedIn Developer Portal — create an app
      2. Generate OAuth 2.0 token with w_member_social scope
      3. GET https://api.linkedin.com/v2/me to find your URN
      4. Set LINKEDIN_ACCESS_TOKEN and LINKEDIN_PERSON_URN in .env
      Note: Tokens expire every 60 days.
    """
    token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    person_urn = os.getenv("LINKEDIN_PERSON_URN")

    if not token or not person_urn or person_urn == "urn:li:person:XXXXXXX":
        print("LinkedIn not configured. Set LINKEDIN_ACCESS_TOKEN and LINKEDIN_PERSON_URN in .env")
        return False

    post_text = linkedin_post if linkedin_post else _format_linkedin_post(topic, full_content, summary)

    # Try to upload image if provided
    asset_urn = None
    if image_path and os.path.exists(image_path):
        asset_urn = _upload_image(token, person_urn, image_path)

    headers = _auth_headers(token)

    if asset_urn:
        # Post with image
        payload = {
            "author": person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": post_text},
                    "shareMediaCategory": "IMAGE",
                    "media": [
                        {
                            "status": "READY",
                            "description": {"text": summary[:200]},
                            "media": asset_urn,
                            "title": {"text": topic[:100]},
                        }
                    ],
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }
    else:
        # Text-only post
        payload = {
            "author": person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": post_text},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }

    try:
        response = requests.post(LINKEDIN_API_URL, headers=headers, json=payload, timeout=30)

        if response.status_code in (200, 201):
            post_id = response.headers.get("x-restli-id", "N/A")
            media_type = "with image" if asset_urn else "text only"
            print(f"LinkedIn post created ({media_type}). ID: {post_id}")
            return True
        elif response.status_code == 401:
            print("LinkedIn token expired. Regenerate at the LinkedIn Developer Portal.")
            return False
        else:
            print(f"LinkedIn post failed: {response.status_code} — {response.text}")
            return False

    except Exception as e:
        print(f"LinkedIn post failed: {e}")
        return False
