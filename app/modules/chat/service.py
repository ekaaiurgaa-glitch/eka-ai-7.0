import re
import hashlib
from sqlalchemy.orm import Session
from . import schema, model
from app.ai import governance, gemini_client, system_prompt
from app.db.session import SessionLocal

async def process_chat_query(db: Session, request: schema.ChatQueryRequest, user_id: str) -> schema.ChatQueryResponse:
    """
    Processes a chat query by applying governance gates, calling the LLM,
    and then parsing the structured response.
    """
    # 1. Apply Governance Gates
    governance.domain_gate(request.query)
    governance.context_gate(request.query, request.vehicle.dict() if request.vehicle else None)

    # 2. Call the Gemini client
    prompt = f"""User query: {request.query}
Vehicle context: {request.vehicle.dict() if request.vehicle else 'Not provided'}"""
    system = system_prompt.get_system_prompt()
    raw_response = await gemini_client.call_gemini(prompt, system)

    # Check for API errors
    if raw_response.startswith("Error:"):
        return schema.ChatQueryResponse(
            issue_summary="AI Service Error",
            probable_causes=["The AI service is currently unavailable"],
            diagnostic_steps=["Please try again later"],
            safety_advisory="N/A",
            confidence_level=0.0,
            rag_references=None
        )

    # 3. Parse the structured response
    parsed_response = parse_structured_response(raw_response)

    # 4. Apply Confidence Gate (skip if response is an error message)
    if parsed_response.confidence_level > 0:
        governance.confidence_gate(parsed_response.confidence_level)

    # 5. Log the request and response
    # log_chat_request(db, request, parsed_response, user_id)

    return parsed_response

def parse_structured_response(raw_response: str) -> schema.ChatQueryResponse:
    """
    Parses the raw text response from the LLM into the structured ChatQueryResponse model.
    This is a simple implementation and might need to be more robust in a production environment.
    """
    try:
        summary_match = re.search(r"Issue Summary:\s*(.*)", raw_response)
        causes_match = re.search(r"Probable Causes:\s*([\s\S]*?)Diagnostic Steps:", raw_response)
        steps_match = re.search(r"Diagnostic Steps:\s*([\s\S]*?)Safety Advisory:", raw_response)
        advisory_match = re.search(r"Safety Advisory:\s*(.*)", raw_response)
        confidence_match = re.search(r"Confidence Level:\s*(\d+\.?\d*)\s*%", raw_response)

        summary = summary_match.group(1).strip() if summary_match else "N/A"
        causes = [c.strip() for c in causes_match.group(1).strip().split('- ') if c.strip()] if causes_match else []
        steps = [s.strip() for s in steps_match.group(1).strip().split('1. ') if s.strip()] if steps_match else []
        advisory = advisory_match.group(1).strip() if advisory_match else "N/A"
        confidence = float(confidence_match.group(1)) if confidence_match else 0.0

        return schema.ChatQueryResponse(
            issue_summary=summary,
            probable_causes=causes,
            diagnostic_steps=steps,
            safety_advisory=advisory,
            confidence_level=confidence,
            rag_references=None
        )
    except Exception as e:
        # If parsing fails, return a default error response or re-raise
        print(f"Error parsing LLM response: {e}")
        # For simplicity, returning a default response. A real app might handle this differently.
        return schema.ChatQueryResponse(
            issue_summary="Could not parse the response from the AI model.",
            probable_causes=[],
            diagnostic_steps=[],
            safety_advisory="N/A",
            confidence_level=0.0,
            rag_references=None
        )


def log_chat_request(db: Session, request: schema.ChatQueryRequest, response: schema.ChatQueryResponse, user_id: str):
    """
    Logs the chat request and response to the database.
    """
    query_hash = hashlib.md5(request.query.encode()).hexdigest()
    db_chat_request = model.ChatRequest(
        tenant_id=request.tenant_id,
        user_id=user_id,
        query_hash=query_hash,
        vehicle_json=request.vehicle.dict() if request.vehicle else None,
        response_json=response.dict(),
        confidence=response.confidence_level,
        query_text=request.query
    )
    db.add(db_chat_request)
    db.commit()

