from fastapi import HTTPException
from app.ai import domain_classifier

LLM_CONFIG = {
    "model": "gemini-2.0-flash",
    "temperature": 0.4,
    "top_p": 0.9,
    "thinking_config": {"thinking_budget": 8192},  # HIGH thinking
    "max_output_tokens": 1024,
    "safety_settings": [
        {"category": "HARM_CATEGORY_HATE_SPEECH",       "threshold": "BLOCK_ONLY_HIGH"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
        {"category": "HARM_CATEGORY_HARASSMENT",        "threshold": "BLOCK_ONLY_HIGH"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
    ]
}

async def domain_gate(query: str):
    """Enforce domain lock using ML classifier."""
    is_auto = await domain_classifier.is_automobile_query(query)
    if not is_auto:
        raise HTTPException(status_code=403, detail="DOMAIN_GATE_DENY: Query is not related to automobiles.")

# Placeholder for Permission Gate
# This is mostly handled by FastAPI's dependency injection system with `has_permission` in `security.py`

# Placeholder for Context Gate
def vehicle_context_complete(vehicle_context: dict) -> bool:
    """
    Checks if the vehicle context is complete enough for a diagnosis.
    """
    required_fields = ["make", "model", "year", "fuel_type"]
    return all(field in vehicle_context and vehicle_context[field] for field in required_fields)

def context_gate(query: str, vehicle_context: dict = None):
    """
    If the query seems to need diagnostic information, it checks if the vehicle context is present.
    """
    diagnostic_keywords = ["problem", "issue", "sound", "noise", "grinding", "stopping", "mg", "quote"]
    needs_diagnostic = any(keyword in query.lower() for keyword in diagnostic_keywords)

    if needs_diagnostic and (not vehicle_context or not vehicle_context_complete(vehicle_context)):
        raise HTTPException(status_code=422, detail="CONTEXT_REQUEST: Please provide vehicle make, model, year, and fuel_type for a better diagnosis/quote.")

# Placeholder for Confidence Gate
def confidence_gate(confidence: float):
    if confidence < 90:
        raise HTTPException(status_code=422, detail="REQUEST_CLARIFICATION: Confidence level is below threshold. Please provide more details.")
