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
    """
    Calls the Gemini API with the given prompt and optional system prompt.
    Uses the new google-genai SDK (google.genai).
    """
    try:
        client = get_client()
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.4,
            top_p=0.9,
        ) if system_prompt else types.GenerateContentConfig(
            temperature=0.4,
            top_p=0.9,
        )

        response = await client.aio.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
            config=config,
        )
        return response.text
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return "Error: Could not get a response from the AI model."


async def call_gemini_with_tools(prompt: str, tools: list, system_prompt: str = None):
    """
    Calls the Gemini API with tools (for function calling).
    Uses the new google-genai SDK (google.genai).
    """
    try:
        client = get_client()
        config = types.GenerateContentConfig(
            tools=tools,
            system_instruction=system_prompt,
            temperature=0.4,
            top_p=0.9,
        )
        response = await client.aio.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
            config=config,
        )
        return response.candidates[0].content.parts
    except Exception as e:
        print(f"Error calling Gemini API with tools: {e}")
        return "Error: Could not get a response from the AI model."
