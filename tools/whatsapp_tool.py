import os
from dotenv import load_dotenv

load_dotenv()


def send_whatsapp(topic: str, summary: str, sources: list[str], media_url: str | None = None) -> bool:
    """
    Send blog post summary to WhatsApp via Twilio.
    Returns True on success, False on failure.

    Setup:
    1. Create a Twilio account at twilio.com
    2. Enable WhatsApp Sandbox in the Twilio Console
    3. Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER, TWILIO_TO_NUMBER in .env
    4. Recipient must opt-in by texting the sandbox join keyword once
    """
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_FROM_NUMBER")
    to_number = os.getenv("TWILIO_TO_NUMBER")

    if not all([account_sid, auth_token, from_number, to_number]):
        print("WhatsApp not configured. Add TWILIO_* keys to .env")
        return False

    try:
        from twilio.rest import Client

        formatted_sources = "\n".join(f"  • {s}" for s in sources[:5])
        body = (
            f"*New Wersec Blog Post*\n\n"
            f"*Topic:* {topic}\n\n"
            f"*Summary:*\n{summary}\n\n"
            f"*Sources:*\n{formatted_sources}"
        )

        client = Client(account_sid, auth_token)
        msg_params = {
            "body": body,
            "from_": from_number,
            "to": to_number,
        }
        if media_url:
            msg_params["media_url"] = [media_url]

        message = client.messages.create(**msg_params)
        print(f"WhatsApp sent. SID: {message.sid}")
        return True

    except Exception as e:
        print(f"WhatsApp send failed: {e}")
        return False
