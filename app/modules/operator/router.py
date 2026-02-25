from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from . import schema, tool_handler
from app.core.dependencies import get_db, get_tenant_id
from app.core.security import require_permission

router = APIRouter(prefix="/operator", tags=["Operator"])


@router.post("/execute", response_model=schema.OperatorPreviewResponse)
async def execute_operator_action(
    request: schema.OperatorExecuteRequest,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_permission("can_execute_operator")),
):
    """Parses an intent, generates a preview, persists it, and returns it for confirmation."""
    return await tool_handler.generate_preview(db, request)


@router.post("/confirm", response_model=schema.OperatorExecutionResponse)
async def confirm_operator_action(
    request: schema.OperatorConfirmRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    _: dict = Depends(require_permission("can_execute_operator")),
):
    """Confirms and executes a previously generated action preview."""
    if not request.confirm:
        return schema.OperatorExecutionResponse(
            execution_id=None,
            status="cancelled",
            result={"message": "Action not confirmed."},
        )
    return await tool_handler.execute_tool(db, request.preview_id, request.actor_id, tenant_id)