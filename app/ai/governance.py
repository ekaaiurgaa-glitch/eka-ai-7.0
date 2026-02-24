from fastapi import HTTPException

# Placeholder for Domain Gate
def is_automobile_query(query: str) -> bool:
    """
    Checks if a query is related to automobiles.
    In a real application, this could be a call to a smaller, specialized LLM,
    a keyword-based check, or a more sophisticated classifier.
    """
    # For now, we'll just do a simple keyword check.
    keywords = ["car", "vehicle", "engine", "brake", "transmission", "automobile", "maruti", "tata", "hyundai"]
    return any(keyword in query.lower() for keyword in keywords)

def domain_gate(query: str):
    if not is_automobile_query(query):
        raise HTTPException(status_code=403, detail="DOMAIN_GATE_DENY: Query is not related to automobiles.")

# Placeholder for Permission Gate
# This is mostly handled by FastAPI's dependency injection system with `has_permission` in `security.py`

# Placeholder for Context Gate
def vehicle_context_complete(vehicle_context: dict) -> bool:
    """
    Checks if the vehicle context is complete enough for a diagnosis.
    """
    required_fields = ["make", "model", "year"]
    return all(field in vehicle_context for field in required_fields)

def context_gate(query: str, vehicle_context: dict = None):
    """
    If the query seems to need diagnostic information, it checks if the vehicle context is present.
    """
    diagnostic_keywords = ["problem", "issue", "sound", "noise", "grinding", "stopping"]
    needs_diagnostic = any(keyword in query.lower() for keyword in diagnostic_keywords)

    if needs_diagnostic and (not vehicle_context or not vehicle_context_complete(vehicle_context)):
        raise HTTPException(status_code=422, detail="CONTEXT_REQUEST: Please provide vehicle make, model, and year for a better diagnosis.")

# Placeholder for Confidence Gate
def confidence_gate(confidence: float):
    if confidence < 90:
        raise HTTPException(status_code=422, detail="REQUEST_CLARIFICATION: Confidence level is below threshold. Please provide more details.")
