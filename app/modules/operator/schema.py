from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class OperatorExecuteRequest(BaseModel):
    intent: Optional[str] = None
    args: Optional[dict] = None
    raw_query: Optional[str] = None # Added for NLP intent detection (P1-10)
    tenant_id: str
    actor_id: str
    dry_run: bool = True

class OperatorPreviewResponse(BaseModel):
    preview_id: str
    tool: str
    args: dict
    action_preview: str
    expires_at: datetime

class OperatorConfirmRequest(BaseModel):
    preview_id: str
    confirm: bool
    actor_id: str

class OperatorExecutionResponse(BaseModel):
    execution_id: Optional[str] = None
    status: str
    result: Optional[Any] = None
