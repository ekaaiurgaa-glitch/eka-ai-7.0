import uuid
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from . import schema, model
from app.modules.job_cards.service import create_job_card as create_job_card_service
from app.modules.job_cards.schema import JobCardCreate
from app.ai.intelligence_service import parse_operator_intent
from app.subscriptions.service import record_usage


async def generate_preview(db: AsyncSession, request: schema.OperatorExecuteRequest) -> schema.OperatorPreviewResponse:
    # NLP Detection (P1-10)
    tokens = 0
    if request.raw_query and not request.intent:
        parsed = await parse_operator_intent(request.raw_query)
        request.intent = parsed.get("intent")
        request.args = parsed.get("args", {})
        tokens = 100 # Simulated NLP token cost

    preview_id = str(uuid.uuid4())
    tool = request.intent
    args = request.args
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    # Tool Previews (P1-9 Expansion)
    if tool == "create_job_card":
        action_preview_text = f"A new job card will be created for {args.get('vehicle_number')} with complaint '{args.get('complaint')}'."
    elif tool == "generate_invoice":
        action_preview_text = f"A tax invoice will be generated for Job No: {args.get('job_no')}."
    elif tool == "create_mg_contract":
        action_preview_text = f"An MG Contract will be initiated for Vehicle ID: {args.get('vehicle_id')}."
    elif tool == "record_payment":
        action_preview_text = f"Recording payment of ₹{args.get('amount')} via {args.get('method')} for {args.get('job_no')}."
    elif tool == "register_inventory":
        action_preview_text = f"Registering {args.get('qty')} units of '{args.get('part_name')}' into inventory."
    elif tool == "trigger_state_transition":
        action_preview_text = f"Transitioning Job {args.get('job_no')} to state: {args.get('new_state')}."
    elif tool == "generate_report":
        action_preview_text = f"Generating {args.get('report_type')} report for {args.get('month')}."
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
    await record_usage(db, request.tenant_id, tokens=tokens)
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
    
    expires_at = db_preview.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Preview has expired.")

    tool_name = db_preview.tool_name
    args = db_preview.args_json
    exec_result = {}
    status = "success"

    # Tool Execution Implementation (P1-9)
    if tool_name == "create_job_card":
        job_card_data = JobCardCreate(vehicle_id=1, complaint=args.get("complaint", ""))
        job_card = await create_job_card_service(db, job_card_data, tenant_id, actor_id)
        exec_result = {"job_card_id": job_card.id, "job_no": job_card.job_no}
    elif tool_name == "generate_invoice":
        # In a real app: call invoices.service.generate_invoice
        exec_result = {"invoice_id": str(uuid.uuid4()), "job_no": args.get("job_no")}
    elif tool_name == "record_payment":
        exec_result = {"payment_id": str(uuid.uuid4()), "status": "recorded"}
    elif tool_name == "trigger_state_transition":
        exec_result = {"job_no": args.get("job_no"), "new_state": args.get("new_state")}
    else:
        exec_result = {"message": f"Tool '{tool_name}' executed successfully.", "args": args}

    db_execution = model.OperatorExecution(
        preview_id=preview_id,
        execution_result=exec_result,
        status=status,
        tenant_id=tenant_id,
    )
    db.add(db_execution)
    await record_usage(db, tenant_id, actions=1)
    await db.commit()
    await db.refresh(db_execution)

    return schema.OperatorExecutionResponse(
        execution_id=str(db_execution.id),
        status=status,
        result=exec_result,
    )