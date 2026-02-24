"""AI-powered job card summarization with safety floor for urgency."""
import json
from typing import Dict, Literal
from app.ai.gemini_client import call_gemini

# Safety floor: keyword-based urgency that AI cannot override downward
URGENCY_KEYWORDS = {
    "critical": ["brake failure", "engine seizure", "fire", "safety critical", "airbag", "fuel leak"],
    "high": ["brake", "steering", "engine noise", "overheating", "transmission", "won't start"],
    "medium": ["service", "oil change", "tire", "alignment", "filter", "check"],
    "low": ["cosmetic", "cleaning", "polish", "detail"],
}


def _compute_keyword_urgency(mechanic_notes: str) -> Literal["critical", "high", "medium", "low"]:
    """Compute minimum urgency from keyword matching."""
    notes_lower = mechanic_notes.lower()
    for level in ["critical", "high", "medium", "low"]:
        if any(kw in notes_lower for kw in URGENCY_KEYWORDS[level]):
            return level
    return "low"


def _max_urgency(a: str, b: str) -> str:
    """Return the more urgent of two urgency levels."""
    order = ["low", "medium", "high", "critical"]
    return a if order.index(a) > order.index(b) else b


def _parse_gemini_response(text: str) -> Dict:
    """Parse Gemini JSON response with fallback for malformed output."""
    try:
        # Try to extract JSON from markdown code blocks
        if "```json" in text:
            json_str = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            json_str = text.split("```")[1].split("```")[0].strip()
        else:
            json_str = text.strip()
        
        data = json.loads(json_str)
        return {
            "technical_summary": data.get("technical_summary", "No technical summary available."),
            "customer_summary": data.get("customer_summary", "No customer summary available."),
            "urgency": data.get("urgency", "medium"),
            "estimated_cost": float(data.get("estimated_cost", 0)),
            "recommended_action": data.get("recommended_action", "Schedule service at earliest convenience."),
        }
    except (json.JSONDecodeError, ValueError, IndexError):
        # Fallback for malformed AI response
        return {
            "technical_summary": "Unable to parse AI response. Please review mechanic notes directly.",
            "customer_summary": "We're analyzing your vehicle's service needs. Our team will contact you shortly with details.",
            "urgency": "medium",
            "estimated_cost": 0.0,
            "recommended_action": "Contact workshop for detailed assessment.",
        }


async def summarize_job_card(
    job_no: str,
    mechanic_notes: str,
    vehicle_info: Dict,
    estimate_parts: list = None,
    estimate_total: float = 0.0,
) -> Dict:
    """
    Generate AI summary of job card with safety floor for urgency.
    
    The safety floor ensures AI cannot downgrade urgency below keyword-detected level.
    """
    # Compute floor urgency from keywords
    keyword_urgency = _compute_keyword_urgency(mechanic_notes)
    
    # Build prompt
    prompt = f"""Analyze this vehicle service job and provide a structured summary.

Job Number: {job_no}
Vehicle: {vehicle_info.get('make', 'Unknown')} {vehicle_info.get('model', 'Unknown')} ({vehicle_info.get('year', 'N/A')})
Mechanic Notes: {mechanic_notes}
Estimated Parts: {estimate_parts or []}
Estimated Total: ₹{estimate_total}

Provide a JSON response with these fields:
- technical_summary: Brief technical summary for mechanics (2-3 sentences)
- customer_summary: Plain-English explanation for vehicle owner (2-3 sentences, reassuring tone)
- urgency: One of [low, medium, high, critical] based on safety impact
- estimated_cost: Estimated repair cost in INR (number only)
- recommended_action: Clear next step for the customer

Example:
{{
  "technical_summary": "Brake pads at 2.3mm, replacement recommended.",
  "customer_summary": "Your brake pads are wearing thin and should be replaced soon for safety.",
  "urgency": "high",
  "estimated_cost": 4500,
  "recommended_action": "Schedule brake pad replacement within 2 weeks."
}}
"""
    
    try:
        # Call Gemini
        response_text = await call_gemini(
            prompt=prompt,
            system_prompt="You are an expert automotive service advisor. Be accurate, reassuring, and safety-conscious."
        )
        
        # Parse response
        result = _parse_gemini_response(response_text)
        
        # Apply safety floor: AI urgency cannot be lower than keyword urgency
        ai_urgency = result.get("urgency", "medium")
        final_urgency = _max_urgency(keyword_urgency, ai_urgency)
        result["urgency"] = final_urgency
        
        return result
        
    except Exception as e:
        # Complete fallback if Gemini fails
        return {
            "technical_summary": f"Service job {job_no} requires attention. Please review mechanic notes.",
            "customer_summary": "Your vehicle has been assessed by our team. We recommend scheduling the recommended service soon.",
            "urgency": keyword_urgency,
            "estimated_cost": estimate_total,
            "recommended_action": "Contact workshop to discuss service options and schedule.",
            "_error": str(e),
        }
