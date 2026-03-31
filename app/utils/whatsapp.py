import os

from twilio.rest import Client


def send_whatsapp_message(phone: str, message: str) -> bool:
    """Send a WhatsApp message via Twilio.

    Returns True when a message is sent, False when configuration is missing
    or sending fails.
    """
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_PHONE_NUMBER")

    if not all([account_sid, auth_token, from_number]):
        return False

    try:
        client = Client(account_sid, auth_token)
        to_number = phone if phone.startswith("whatsapp:") else f"whatsapp:{phone}"
        from_number = (
            from_number if from_number.startswith("whatsapp:") else f"whatsapp:{from_number}"
        )
        client.messages.create(body=message, from_=from_number, to=to_number)
        return True
    except Exception:
        return False
