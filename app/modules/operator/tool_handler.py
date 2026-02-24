import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from . import schema, model
from app.modules.job_cards.service import create_job_card as create_job_card_service
from app.modules.job_cards.schema import JobCardCreate
from app.db.session import SessionLocal

def generate_preview(db: Session, request: schema.OperatorExecuteRequest) -> schema.OperatorPreviewResponse:
    """
    Generates a preview of the action to be executed and stores it in the database.
    """
    preview_id = str(uuid.uuid4())
    tool = request.intent
    args = request.args
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    if tool == "create_job_card":
        action_preview_text = f"A new job card will be created for {args.get('vehicle_number')} with complaint '{args.get('complaint')}'. No irreversible action will be executed without explicit confirmation. Please confirm to proceed."
    else:
        action_preview_text = "This is a preview of the action."

    preview_response = schema.OperatorPreviewResponse(
        preview_id=preview_id,
        tool=tool,
        args=args,
        action_preview=action_preview_text,
        expires_at=expires_at,
    )

    # db_preview = model.OperatorPreview(
    #     id=preview_id,
    #     tenant_id=request.tenant_id,
    #     actor_id=request.actor_id,
    #     tool_name=tool,
    #     args_json=args,
    #     preview_json=preview_response.dict(),
    #     expires_at=expires_at
    # )
    # db.add(db_preview)
    # db.commit()

    return preview_response

def execute_tool(db: Session, preview_id: str, actor_id: str, tenant_id: str) -> schema.OperatorExecutionResponse:
    """
    Executes the tool associated with the preview.
    """
    db_preview = db.query(model.OperatorPreview).filter(model.OperatorPreview.id == preview_id, model.OperatorPreview.tenant_id == tenant_id).first()

    if not db_preview or db_preview.expires_at < datetime.utcnow():
        return schema.OperatorExecutionResponse(execution_id=str(uuid.uuid4()), status="error", result={"message": "Preview not found or expired."})

    # In a real app, you would also check if the actor_id matches the one who initiated the preview.

    tool_name = db_preview.tool_name
    args = db_preview.args_json

    result = {}
    status = "error"

    if tool_name == "create_job_card":
        job_card_data = JobCardCreate(vehicle_id=1, complaint=args.get('complaint')) # vehicle_id is placeholder
        job_card = create_job_card_service(db, job_card_data, tenant_id, actor_id)
        result = {"job_card_id": job_card.id}
        status = "success"
    else:
        result = {"message": "Tool not implemented."}

    db_execution = model.OperatorExecution(
        preview_id=preview_id,
        execution_result=result,
        status=status,
        tenant_id=tenant_id
    )
    db.add(db_execution)
    db.commit()
    db.refresh(db_execution)

    return schema.OperatorExecutionResponse(
        execution_id=str(db_execution.id),
        status=status,
        result=result
    )