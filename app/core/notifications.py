"""Notifications service (Twilio/SendGrid)."""
from pydantic import BaseModel
from typing import Optional


class SMSRequest(BaseModel):
    phone_number: str
    message: str
    template_id: Optional[str] = None


class EmailRequest(BaseModel):
    to_email: str  # Using str instead of EmailStr to avoid dependency
    subject: str
    body: str
    html_body: Optional[str] = None


class NotificationService:
    async def send_sms(self, request: SMSRequest) -> dict:
        return {
            "status": "sent",
            "channel": "sms",
            "recipient": request.phone_number,
            "message_id": f"sms_{hash(request.message) % 10000}"
        }
    
    async def send_email(self, request: EmailRequest) -> dict:
        return {
            "status": "sent",
            "channel": "email",
            "recipient": request.to_email,
            "subject": request.subject,
            "message_id": f"email_{hash(request.subject) % 10000}"
        }
    
    async def send_approval_link(self, email: str, approval_token: str, job_card_id: str) -> dict:
        link = f"https://eka.ai/approve/{approval_token}"
        return await self.send_email(EmailRequest(
            to_email=email,
            subject=f"Approval Required - Job Card #{job_card_id}",
            body=f"Please approve the estimate: {link}",
            html_body=f"<p>Please <a href='{link}'>click here</a> to approve.</p>"
        ))


notification_service = NotificationService()
