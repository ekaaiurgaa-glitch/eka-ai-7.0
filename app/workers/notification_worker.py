import logging
import asyncio

logger = logging.getLogger(__name__)

async def send_notification(payload: dict):
    """
    Handles notifications from RabbitMQ.
    Routes to SMS (Twilio) or Email (SendGrid).
    Payload format:
    {
        "channel": "sms" | "email",
        "to": "+919876543210" | "user@example.com",
        "subject": "Approval Request", # only for email
        "body": "Please approve your estimate using this link: ..."
    }
    """
    channel = payload.get("channel")
    to_address = payload.get("to")
    
    logger.info(f"Sending {channel} notification to {to_address}")
    # Mocking successful dispatch
    await asyncio.sleep(0.5)
    return True
