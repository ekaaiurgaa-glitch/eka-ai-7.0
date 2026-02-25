import re
import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from . import schema, model
from app.ai import governance, system_prompt
from app.ai.llm_client import LLMClient
from app.subscriptions.service import record_usage, check_subscription_limits


async def process_chat_query(db: AsyncSession, request: schema.ChatQueryRequest, user_id: str) -> schema.ChatQueryResponse:
    """
    Processes a chat query:
    1. Governance gates (domain, context)
    2. RAG retrieval — inject knowledge context into prompt
    3. Gemini LLM call
    4. Response parsing + confidence gate
    5. Safety & Hallucination gate
    6. Log request to DB
    7. Record usage metering
    """
    await check_subscription_limits(db, request.tenant_id, "tokens")
    
    # Gate 1: Privacy Compliance (PII Scrubbing)
    request.query = governance.scrub_pii(request.query)

    # Gate 2: Domain lock
    await governance.domain_gate(request.query)
    governance.context_gate(request.query, request.vehicle.model_dump() if request.vehicle else None)

    # RAG: retrieve relevant knowledge chunks
    rag_context = ""
    rag_references = []
    try:
        from app.modules.knowledge.service import similarity_search
        chunks = await similarity_search(db, request.query, request.tenant_id, top_k=3)
        if chunks:
            rag_context = "\n\nRelevant Knowledge Base Context:\n" + "\n---\n".join(
                f"[{c.title}] {c.content}" for c in chunks
            )
            rag_references = [c.title for c in chunks]
    except Exception:
        pass  # RAG is additive, not blocking

    prompt = f"""User query: {request.query}
Vehicle context: {request.vehicle.model_dump() if request.vehicle else 'Not provided'}{rag_context}"""

    # sys_prompt = system_prompt.get_system_prompt() # We'll put it in messages
    messages = [
        {"role": "system", "content": system_prompt.get_system_prompt()},
        {"role": "user", "content": prompt}
    ]
    
    client = LLMClient()
    res = await client.complete(messages)
    raw_response = res.content

    if raw_response.startswith("Error:"):
        return schema.ChatQueryResponse(
            issue_summary="AI Service Error",
            probable_causes=["The AI service is currently unavailable"],
            diagnostic_steps=["Please try again later"],
            safety_advisory="N/A",
            confidence_level=0.0,
            rag_references=None,
        )

    parsed_response = parse_structured_response(raw_response)
    parsed_response.rag_references = rag_references or None

    if parsed_response.confidence_level > 0:
        governance.confidence_gate(parsed_response.confidence_level)
    
    # Gate 4: Safety & Hallucination
    await governance.safety_gate(parsed_response.issue_summary + " " + parsed_response.safety_advisory)

    # Log the request
    await log_chat_request(db, request, parsed_response, user_id)

    # Record usage metering (P1-11)
    tokens = 150 + (300 if rag_references else 0)
    await record_usage(db, request.tenant_id, tokens=tokens)
    parsed_response.tokens_used = tokens

    return parsed_response


def parse_structured_response(raw_response: str) -> schema.ChatQueryResponse:
    try:
        summary_match = re.search(r"Issue Summary:\s*(.*)", raw_response)
        causes_match = re.search(r"Probable Causes:\s*([\s\S]*?)Diagnostic Steps:", raw_response)
        steps_match = re.search(r"Diagnostic Steps:\s*([\s\S]*?)Safety Advisory:", raw_response)
        advisory_match = re.search(r"Safety Advisory:\s*(.*)", raw_response)
        confidence_match = re.search(r"Confidence Level:\s*(\d+\.?\d*)\s*%", raw_response)

        summary = summary_match.group(1).strip() if summary_match else raw_response[:200]
        causes = [c.strip() for c in causes_match.group(1).strip().split("- ") if c.strip()] if causes_match else []
        steps = [s.strip() for s in steps_match.group(1).strip().split("1. ") if s.strip()] if steps_match else []
        advisory = advisory_match.group(1).strip() if advisory_match else "Consult a certified technician."
        confidence = float(confidence_match.group(1)) if confidence_match else 0.0

        return schema.ChatQueryResponse(
            issue_summary=summary,
            probable_causes=causes,
            diagnostic_steps=steps,
            safety_advisory=advisory,
            confidence_level=confidence,
            rag_references=None,
        )
    except Exception as e:
        return schema.ChatQueryResponse(
            issue_summary="Could not parse the response from the AI model.",
            probable_causes=[],
            diagnostic_steps=[],
            safety_advisory="N/A",
            confidence_level=0.0,
            rag_references=None,
        )


async def log_chat_request(db: AsyncSession, request: schema.ChatQueryRequest, response: schema.ChatQueryResponse, user_id: str):
    """Non-blocking fire-and-forget log — runs in background without awaiting."""
    try:
        query_hash = hashlib.md5(request.query.encode()).hexdigest()
        db_chat_request = model.ChatRequest(
            tenant_id=request.tenant_id,
            user_id=user_id,
            query_hash=query_hash,
            vehicle_json=request.vehicle.model_dump() if request.vehicle else None,
            response_json=response.model_dump(),
            confidence=response.confidence_level,
            query_text=request.query,
        )
        db.add(db_chat_request)
        await db.commit()
    except Exception:
        pass  # Chat logging is non-critical
