import os
import requests
from dotenv import load_dotenv

load_dotenv()

LINKEDIN_API_URL = "https://api.linkedin.com/v2/ugcPosts"


def _format_linkedin_post(topic: str, full_content: str, summary: str) -> str:
    """Format blog content for LinkedIn (max 3000 chars, no markdown)."""
    hashtags = "\n\n#Cybersecurity #InfoSec #AI #Wersec #LinkedIn"
    header = f"{topic}\n\n"
    body = summary + "\n\n"

    # Extract first few sections from full_content (strip markdown)
    lines = full_content.split("\n")
    clean_lines = []
    for line in lines:
        line = line.strip()
        if line.startswith("#"):
            line = line.lstrip("#").strip()
        if line and not line.startswith("```"):
            clean_lines.append(line)
        if len("\n".join(clean_lines)) > 1800:
            break

    body += "\n".join(clean_lines[:20])
    post = header + body + hashtags
    return post[:3000]


def post_to_linkedin(topic: str, full_content: str, summary: str, linkedin_post: str = "") -> bool:
    """
    Post blog to LinkedIn as a text update.
    Returns True on success, False on failure.

    Setup:
    1. Go to LinkedIn Developer Portal and create an app
    2. Generate an OAuth 2.0 access token with w_member_social scope
    3. Get your URN via: GET https://api.linkedin.com/v2/me
    4. Set LINKEDIN_ACCESS_TOKEN and LINKEDIN_PERSON_URN in .env
    Note: Tokens expire after 60 days — regenerate when expired.
    """
    token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    person_urn = os.getenv("LINKEDIN_PERSON_URN")

    if not all([token, person_urn]):
        print("LinkedIn not configured. Add LINKEDIN_ACCESS_TOKEN and LINKEDIN_PERSON_URN to .env")
        return False

    try:
        post_text = linkedin_post if linkedin_post else _format_linkedin_post(topic, full_content, summary)

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }

        payload = {
            "author": person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": post_text},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            },
        }

        response = requests.post(LINKEDIN_API_URL, headers=headers, json=payload, timeout=30)

        if response.status_code in (200, 201):
            print(f"LinkedIn post created. ID: {response.headers.get('x-restli-id', 'N/A')}")
            return True
        elif response.status_code == 401:
            print("LinkedIn token expired. Regenerate it at the LinkedIn Developer Portal.")
            return False
        else:
            print(f"LinkedIn post failed: {response.status_code} — {response.text}")
            return False

    except Exception as e:
        print(f"LinkedIn post failed: {e}")
        return False
