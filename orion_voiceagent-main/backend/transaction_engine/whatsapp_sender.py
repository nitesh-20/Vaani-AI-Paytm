"""
whatsapp_sender.py — Send WhatsApp messages via Twilio sandbox.

Requires env vars:
  TWILIO_ACCOUNT_SID
  TWILIO_AUTH_TOKEN
  TWILIO_WHATSAPP_FROM  (default: whatsapp:+14155238886 — Twilio sandbox)
  WHATSAPP_TO           (e.g. whatsapp:+91XXXXXXXXXX)
"""
import logging
import os

logger = logging.getLogger(__name__)


def send_whatsapp(message_text: str) -> bool:
    """
    Send a WhatsApp text message to WHATSAPP_TO using Twilio.
    Returns True on success, False on failure.
    """
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN", "")
    from_number = os.environ.get("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
    to_number = os.environ.get("WHATSAPP_TO", "")

    if not all([account_sid, auth_token, to_number]):
        logger.warning("Twilio credentials or WHATSAPP_TO not configured — skipping send")
        return False

    try:
        from twilio.rest import Client  # lazy import — only needed at send time
        client = Client(account_sid, auth_token)
        client.messages.create(
            from_=from_number,
            body=message_text,
            to=to_number,
        )
        logger.info("WhatsApp message sent to %s", to_number)
        return True
    except Exception as e:
        logger.error("Failed to send WhatsApp message: %s", e)
        return False
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
