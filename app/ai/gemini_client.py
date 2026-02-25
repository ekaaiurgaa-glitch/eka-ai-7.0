from google import genai
from google.genai import types
from app.core.config import settings

_client = None

def get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


async def call_gemini(prompt: str, system_prompt: str = None) -> str:
    """TDD Compliant: gemini-2.0-flash, temp=0.4, top_p=0.9, max_tokens=1024, safety=BLOCK_ONLY_HIGH"""
    try:
        client = get_client()
        
        safety_settings = [
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_ONLY_HIGH"),
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_ONLY_HIGH"),
            types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_ONLY_HIGH"),
            types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_ONLY_HIGH")
        ]
        
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.4,
            top_p=0.9,
            max_output_tokens=1024,
            safety_settings=safety_settings
        ) if system_prompt else types.GenerateContentConfig(
            temperature=0.4,
            top_p=0.9,
            max_output_tokens=1024,
            safety_settings=safety_settings
        )

        response = await client.aio.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=config,
        )
        return response.text
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return "Error: Could not get a response from the AI model."


async def call_gemini_with_tools(prompt: str, tools: list, system_prompt: str = None):
    """TDD Compliant: gemini-2.0-flash, temp=0.4, top_p=0.9, max_tokens=1024, safety=BLOCK_ONLY_HIGH"""
    try:
        client = get_client()
        
        safety_settings = [
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_ONLY_HIGH"),
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_ONLY_HIGH"),
            types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_ONLY_HIGH"),
            types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_ONLY_HIGH")
        ]
        
        config = types.GenerateContentConfig(
            tools=tools,
            system_instruction=system_prompt,
            temperature=0.4,
            top_p=0.9,
            max_output_tokens=1024,
            safety_settings=safety_settings
        )
        
        response = await client.aio.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=config,
        )
        return response.candidates[0].content.parts
    except Exception as e:
        print(f"Error calling Gemini API with tools: {e}")
        return "Error: Could not get a response from the AI model."
