"""Payment gateway integration (Stripe/Razorpay)."""
from typing import Optional
from pydantic import BaseModel
import os


class PaymentRequest(BaseModel):
    amount: float
    currency: str = "INR"
    customer_email: str
    description: str
    metadata: Optional[dict] = None


class PaymentResponse(BaseModel):
    payment_id: str
    status: str
    amount: float
    payment_url: Optional[str] = None


class PaymentGateway:
    def __init__(self):
        self.provider = os.getenv("PAYMENT_PROVIDER", "razorpay")
        self.api_key = os.getenv("PAYMENT_API_KEY")
        self.api_secret = os.getenv("PAYMENT_API_SECRET")
    
    async def create_payment(self, request: PaymentRequest) -> PaymentResponse:
        if self.provider == "razorpay":
            return await self._razorpay_create(request)
        elif self.provider == "stripe":
            return await self._stripe_create(request)
        raise ValueError(f"Unsupported provider: {self.provider}")
    
    async def _razorpay_create(self, request: PaymentRequest) -> PaymentResponse:
        try:
            import razorpay
            client = razorpay.Client(auth=(self.api_key, self.api_secret))
            order = client.order.create({
                "amount": int(request.amount * 100),
                "currency": request.currency,
                "notes": request.metadata or {}
            })
            return PaymentResponse(
                payment_id=order["id"],
                status="created",
                amount=request.amount,
                payment_url=f"https://razorpay.com/checkout/{order['id']}"
            )
        except ImportError:
            return PaymentResponse(
                payment_id="mock_razorpay_" + str(int(request.amount)),
                status="mock",
                amount=request.amount
            )
    
    async def _stripe_create(self, request: PaymentRequest) -> PaymentResponse:
        try:
            import stripe
            stripe.api_key = self.api_key
            intent = stripe.PaymentIntent.create(
                amount=int(request.amount * 100),
                currency=request.currency.lower(),
                description=request.description,
                metadata=request.metadata or {}
            )
            return PaymentResponse(
                payment_id=intent.id,
                status=intent.status,
                amount=request.amount,
                payment_url=intent.client_secret
            )
        except ImportError:
            return PaymentResponse(
                payment_id="mock_stripe_" + str(int(request.amount)),
                status="mock",
                amount=request.amount
            )
    
    async def verify_payment(self, payment_id: str) -> dict:
        if self.provider == "razorpay":
            try:
                import razorpay
                client = razorpay.Client(auth=(self.api_key, self.api_secret))
                payment = client.payment.fetch(payment_id)
                return {"status": payment["status"], "amount": payment["amount"] / 100}
            except:
                return {"status": "mock", "amount": 0}
        elif self.provider == "stripe":
            try:
                import stripe
                stripe.api_key = self.api_key
                intent = stripe.PaymentIntent.retrieve(payment_id)
                return {"status": intent.status, "amount": intent.amount / 100}
            except:
                return {"status": "mock", "amount": 0}
        return {"status": "unknown", "amount": 0}


gateway = PaymentGateway()
