"""Notifications service (Twilio/SendGrid)."""
import logging
from pydantic import BaseModel
from typing import Optional
from twilio.rest import Client as TwilioClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.core.config import settings

logger = logging.getLogger(__name__)

class SMSRequest(BaseModel):
    phone_number: str
    message: str
    template_id: Optional[str] = None


class EmailRequest(BaseModel):
    to_email: str
    subject: str
    body: str
    html_body: Optional[str] = None


class NotificationService:
    def __init__(self):
        self.twilio_client = None
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            self.twilio_client = TwilioClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        self.sendgrid_client = None
        if settings.SENDGRID_API_KEY:
            self.sendgrid_client = SendGridAPIClient(settings.SENDGRID_API_KEY)

    async def send_sms(self, request: SMSRequest) -> dict:
        if self.twilio_client and settings.TWILIO_FROM_NUMBER:
            try:
                message = self.twilio_client.messages.create(
                    body=request.message,
                    from_=settings.TWILIO_FROM_NUMBER,
                    to=request.phone_number
                )
                return {"status": "sent", "message_id": message.sid}
            except Exception as e:
                logger.error(f"Failed to send SMS via Twilio: {e}")
                return {"status": "failed", "error": str(e)}
        
        logger.info(f"[MOCK SMS] To: {request.phone_number}, Msg: {request.message}")
        return {
            "status": "sent",
            "channel": "sms",
            "recipient": request.phone_number,
            "message_id": "mock_sms_123"
        }
    
    async def send_email(self, request: EmailRequest) -> dict:
        if self.sendgrid_client:
            try:
                message = Mail(
                    from_email=settings.FROM_EMAIL,
                    to_emails=request.to_email,
                    subject=request.subject,
                    plain_text_content=request.body,
                    html_content=request.html_body or request.body
                )
                response = self.sendgrid_client.send(message)
                return {"status": "sent", "status_code": response.status_code}
            except Exception as e:
                logger.error(f"Failed to send Email via SendGrid: {e}")
                return {"status": "failed", "error": str(e)}

        logger.info(f"[MOCK EMAIL] To: {request.to_email}, Subject: {request.subject}")
        return {
            "status": "sent",
            "channel": "email",
            "recipient": request.to_email,
            "subject": request.subject,
            "message_id": "mock_email_123"
        }
    
    async def send_approval_link(self, email: str, job_no: str, estimate_id: int) -> dict:
        # In a real app, you'd generate a signed token/URL
        link = f"https://eka.ai/approve/est_{estimate_id}"
        return await self.send_email(EmailRequest(
            to_email=email,
            subject=f"Approval Required - Job Card {job_no}",
            body=f"Your estimate for {job_no} is ready. Please approve it here: {link}",
            html_body=f"""
                <h3>Estimate Ready for Approval</h3>
                <p>Your vehicle's estimate for Job Card <strong>{job_no}</strong> is ready for your review.</p>
                <p>Please click the link below to view and approve:</p>
                <a href="{link}" style="padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px;">View Estimate</a>
            """
        ))


notification_service = NotificationService()
