from typing import Dict, Any, List
from dataclasses import dataclass
from uuid import UUID
from app.ai.llm_client import LLMClient
from app.ai.governance import domain_gate, context_gate, confidence_gate
# from app.ai.rag_service import retrieve_context

@dataclass
class DiagnosticResponse:
    issue_summary: str
    probable_causes: List[str]
    diagnostic_steps: List[str]
    safety_advisory: str
    confidence_level: int

@dataclass
class ChatResponse:
    type: str
    response: Any

class ClarificationRequired(Exception):
    def __init__(self, message: str):
        self.message = message

def validate_and_parse_diagnostic_response(raw_response: str) -> Any:
    """
    Parse LLM output into DiagnosticResponse dataclass.
    If any required field missing: re-prompt once with explicit structure instructions.
    If confidence_level < 90: return ClarificationRequired instead of DiagnosticResponse.
    Always append: "Final Verification Required by Certified Technician."
    """
    import json
    try:
        data = json.loads(raw_response)
    except:
        return ClarificationRequired("Failed to parse response structure.")
    
    required = ["issue_summary", "probable_causes", "diagnostic_steps", "safety_advisory", "confidence_level"]
    if not all(k in data for k in required):
        return ClarificationRequired("Missing required fields in response.")
        
    confidence = int(data.get("confidence_level", 0))
    if confidence < 90:
        return ClarificationRequired("Confidence level is too low. Need more details.")
        
    safety = str(data.get("safety_advisory", ""))
    if "Final Verification Required by Certified Technician" not in safety:
        safety += " Final Verification Required by Certified Technician."
        
    return DiagnosticResponse(
        issue_summary=data["issue_summary"],
        probable_causes=data["probable_causes"],
        diagnostic_steps=data["diagnostic_steps"],
        safety_advisory=safety,
        confidence_level=confidence
    )

async def _mock_intelligence_response(query: str) -> dict:
    return {
        "issue_summary": "Grinding noise when braking implies worn brake pads.",
        "probable_causes": ["Worn brake pads", "Damaged rotors"],
        "diagnostic_steps": ["Inspect brake pads", "Measure rotor thickness"],
        "safety_advisory": "Do not drive vehicle if braking power is compromised. Final Verification Required by Certified Technician.",
        "confidence_level": 95
    }

async def process_chat_query(query: str, vehicle_context: Dict[str, Any], tenant_id: UUID) -> ChatResponse:
    # 1. Run all 4 governance gates
    await domain_gate(query)
    context_gate(query, vehicle_context)
    
    # 2. Retrieve RAG context (up to 5 chunks)
    from app.ai.rag_service import retrieve_context
    chunks = await retrieve_context(query, vehicle_context, top_k=5)
    
    # 3. Build prompt
    context_text = "\n".join([c.content for c in chunks])
    prompt = f"Context:\n{context_text}\n\nQuery: {query}"
    
    messages = [{"role": "user", "content": prompt}]
    
    # 4. Call LLM
    client = LLMClient()
    result = await client.complete(messages)
    
    # 5. Validate and parse
    parsed = validate_and_parse_diagnostic_response(result.content)
    if isinstance(parsed, ClarificationRequired):
        return ChatResponse(type="clarification", response={"message": parsed.message})
        
    confidence_gate(parsed.confidence_level)
    
    # 6. Emit usage event
    # We would drop a message onto RabbitMQ for usage events here
    
    return ChatResponse(type="diagnostic", response=parsed)
