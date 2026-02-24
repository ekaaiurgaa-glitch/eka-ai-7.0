import google.generativeai as genai
from app.core.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

# This is a placeholder. In a real application, you would have more robust error handling and logging.
async def call_gemini(prompt: str, system_prompt: str = None):
    """
    Calls the Gemini API with the given prompt and system prompt.
    """
    try:
        model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_prompt)
        response = await model.generate_content_async(prompt)
        return response.text
    except Exception as e:
        # In a real app, you would have more specific error handling
        # and probably log the error.
        print(f"Error calling Gemini API: {e}")
        return "Error: Could not get a response from the AI model."

async def call_gemini_with_tools(prompt: str, tools: list, system_prompt: str = None):
    """
    Calls the Gemini API with tools (for function calling).
    """
    try:
        model = genai.GenerativeModel('gemini-2.5-flash', tools=tools, system_instruction=system_prompt)
        response = await model.generate_content_async(prompt)
        return response.candidates[0].content.parts
    except Exception as e:
        print(f"Error calling Gemini API with tools: {e}")
        return "Error: Could not get a response from the AI model."

