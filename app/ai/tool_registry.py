from google.generativeai.types import FunctionDeclaration, Tool

def get_tool_registry():
    """
    Returns a list of tools that the EKA Operator can use.
    """

    create_job_card_tool = FunctionDeclaration(
        name="create_job_card",
        description="Creates a new job card for a vehicle.",
        parameters={
            "type": "object",
            "properties": {
                "vehicle_number": {
                    "type": "string",
                    "description": "The vehicle's registration number.",
                },
                "complaint": {
                    "type": "string",
                    "description": "The customer's complaint or reason for the service.",
                },
                "tenant_id": {
                    "type": "string",
                    "description": "The ID of the tenant.",
                },
            },
            "required": ["vehicle_number", "complaint", "tenant_id"],
        },
    )

    # Add other tools here as they are implemented
    # e.g., generate_invoice_tool, create_mg_contract_tool, etc.

    return [Tool(function_declarations=[create_job_card_tool])]
