from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class OperatorExecuteRequest(BaseModel):
    intent: str
    args: dict
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
    execution_id: str
    status: str
    result: Optional[Any]
