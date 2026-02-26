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
        parts=[types.Part.from_text(text="What is EKA-AI?")],
    ),
]

config = types.GenerateContentConfig(
    temperature=0.4,
    system_instruction=[types.Part.from_text(text="You are EKA-AI, a governed automobile intelligence system.")],
)

print("Response:")
for chunk in client.models.generate_content_stream(
    model=model,
    contents=contents,
    config=config,
):
    if chunk.text:
        print(chunk.text, end="")
print()
