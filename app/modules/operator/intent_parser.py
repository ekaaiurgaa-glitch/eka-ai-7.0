import json
import re
from typing import Dict, Any
from app.ai.llm_client import LLMClient

class IntentParser:
    """
    Dedicated Intent Parser for Operator AI (P1-3).
    Parses natural language queries into structured tool calls.
    """
    
    def __init__(self):
        self.client = LLMClient()
        self.possible_tools = [
            "create_job_card(vehicle_number, complaint)",
            "generate_invoice(job_no)",
            "create_mg_contract(vehicle_id, customer_id)",
            "record_payment(job_no, amount, method)",
            "register_inventory(part_name, qty, price)",
            "generate_report(report_type, month)",
            "trigger_state_transition(job_no, new_state)",
            "add_estimate(job_id, part_desc)"
        ]

    async def parse_query(self, query: str) -> Dict[str, Any]:
        prompt = f"""You are the EKA Operator Parser. Convert natural language into a tool call JSON.
Possible tools: 
{chr(10).join([f"- {t}" for t in self.possible_tools])}

Query: \"{query}\"
Return ONLY JSON. Example: {{"intent": "create_job_card", "args": {{"vehicle_number": "KA01", "complaint": "noise"}}}}
JSON:"""
        
        res = await self.client.complete([{"role": "user", "content": prompt}], temperature=0.1)
        
        try:
            # Extract JSON between curly braces if LLM adds text
            match = re.search(r'(\{.*\})', res.content, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            return json.loads(res.content)
        except (json.JSONDecodeError, AttributeError):
            # Fallback for failed parsing
            return {"intent": "unknown", "args": {"raw_query": query}}

intent_parser = IntentParser()
