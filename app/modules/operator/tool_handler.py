import uuid
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from . import schema, model
from app.modules.job_cards.service import create_job_card as create_job_card_service
from app.modules.job_cards.schema import JobCardCreate


async def generate_preview(db: AsyncSession, request: schema.OperatorExecuteRequest) -> schema.OperatorPreviewResponse:
    preview_id = str(uuid.uuid4())
    tool = request.intent
    args = request.args
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    if tool == "create_job_card":
        action_preview_text = (
            f"A new job card will be created for {args.get('vehicle_number')} "
            f"with complaint '{args.get('complaint')}'. "
            "No irreversible action will be executed without explicit confirmation. "
            "Please confirm to proceed."
        )
    else:
        action_preview_text = f"Preview for action: {tool}. Please confirm to proceed."

    preview_response = schema.OperatorPreviewResponse(
        preview_id=preview_id,
        tool=tool,
        args=args,
        action_preview=action_preview_text,
        expires_at=expires_at,
    )

    db_preview = model.OperatorPreview(
        id=preview_id,
        tenant_id=request.tenant_id,
        actor_id=request.actor_id,
        tool_name=tool,
        args_json=args,
        preview_json=preview_response.model_dump(mode="json"),
        expires_at=expires_at,
    )
    db.add(db_preview)
    await db.commit()

    return preview_response


async def execute_tool(db: AsyncSession, preview_id: str, actor_id: str, tenant_id: str) -> schema.OperatorExecutionResponse:
    result = await db.execute(
        select(model.OperatorPreview).filter(
            model.OperatorPreview.id == preview_id,
            model.OperatorPreview.tenant_id == tenant_id,
        )
    )
    db_preview = result.scalar_one_or_none()

    if not db_preview:
        raise HTTPException(status_code=404, detail="Preview not found.")
    
    # Handle timezone comparison (SQLite stores naive datetimes)
    expires_at = db_preview.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Preview has expired.")

    tool_name = db_preview.tool_name
    args = db_preview.args_json
    exec_result = {}
    status = "error"

    if tool_name == "create_job_card":
        job_card_data = JobCardCreate(vehicle_id=1, complaint=args.get("complaint", ""))
        job_card = await create_job_card_service(db, job_card_data, tenant_id, actor_id)
        exec_result = {"job_card_id": job_card.id, "job_no": job_card.job_no}
        status = "success"
    else:
        exec_result = {"message": f"Tool '{tool_name}' not yet implemented."}

    db_execution = model.OperatorExecution(
        preview_id=preview_id,
        execution_result=exec_result,
        status=status,
        tenant_id=tenant_id,
    )
    db.add(db_execution)
    await db.commit()
    await db.refresh(db_execution)

    return schema.OperatorExecutionResponse(
        execution_id=str(db_execution.id),
        status=status,
        result=exec_result,
    )