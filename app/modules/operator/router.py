from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from . import schema, tool_handler
from app.core.dependencies import get_db

router = APIRouter()

@router.post("/operator/execute", response_model=schema.OperatorPreviewResponse)
def execute_operator_action(
    request: schema.OperatorExecuteRequest,
    db: Session = Depends(get_db)
):
    """
    Parses an intent, generates a preview, and returns it for confirmation.
    If `dry_run` is false, it would attempt to execute directly, but the
    recommended flow is to always generate a preview first.
    """
    return tool_handler.generate_preview(db, request)

@router.post("/operator/confirm", response_model=schema.OperatorExecutionResponse)
def confirm_operator_action(
    request: schema.OperatorConfirmRequest,
    db: Session = Depends(get_db)
):
    """
    Confirms and executes a previously generated action preview.
    """
    tenant_id = "some_tenant_id" # This should be extracted from the user's token or context
    if not request.confirm:
        return schema.OperatorExecutionResponse(
            execution_id=None,
            status="cancelled",
            result={"message": "Action not confirmed."}
        )

    return tool_handler.execute_tool(db, request.preview_id, request.actor_id, tenant_id)