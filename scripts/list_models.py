import os
from google import genai
from pathlib import Path

# Read API key from .env
env_file = Path('.env')
for line in env_file.read_text().splitlines():
    if line.startswith('GEMINI_API_KEY='):
        api_key = line.split('=', 1)[1].strip().strip('"\'')
        break

client = genai.Client(api_key=api_key)
print('Available models:')
for model in client.models.list():
    print(f'  - {model.name}')
