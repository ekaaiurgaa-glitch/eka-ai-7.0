import os
from pathlib import Path
from google import genai
from google.genai import types

# Read API key from .env
env_file = Path('.env')
for line in env_file.read_text().splitlines():
    if line.startswith('GEMINI_API_KEY='):
        api_key = line.split('=', 1)[1].strip().strip('"\'')
        break

client = genai.Client(api_key=api_key)

model = "gemini-2.5-flash"
contents = [
    types.Content(
        role="user",
        parts=[types.Part.from_text(text="Create job card for vehicle MH12AB1234 with brake issue complaint")],
    ),
]

tools = [
    types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="create_job_card",
                description="Create a new job card in the operational engine",
                parameters=genai.types.Schema(
                    type=genai.types.Type.OBJECT,
                    required=["vehicle_number", "complaint"],
                    properties={
                        "vehicle_number": genai.types.Schema(type=genai.types.Type.STRING),
                        "complaint": genai.types.Schema(type=genai.types.Type.STRING),
                    },
                ),
            ),
        ]
    )
]

config = types.GenerateContentConfig(
    temperature=0.4,
    tools=tools,
    system_instruction=[types.Part.from_text(text="You are EKA-AI, a governed automobile intelligence system. When user asks to create a job card, use the create_job_card function.")],
)

print("Response:")
for chunk in client.models.generate_content_stream(
    model=model,
    contents=contents,
    config=config,
):
    if chunk.text:
        print(chunk.text, end="")
    elif chunk.function_calls:
        print(f"\n[Function Call: {chunk.function_calls[0]}]")
print()
