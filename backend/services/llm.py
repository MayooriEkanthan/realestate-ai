import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
# Fallback to backend/.env if running from another directory
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# If you get a "model not found" error, copy a current model name
# from Google AI Studio and paste it here.
MODEL = "gemini-flash-latest"

_client = None


def _get_client():
    global _client
    if _client is None:
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            raise RuntimeError("GEMINI_API_KEY is missing in backend/.env")
        _client = genai.Client(api_key=key)
    return _client


def ask(prompt: str, system: str = "You are a helpful real estate assistant for Sri Lanka.") -> str:
    try:
        response = _get_client().models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(system_instruction=system),
        )
        return response.text or ""
    except Exception as e:
        print("LLM error:", repr(e))  # shows the real error in your terminal
        return f"Sorry, the AI service is unavailable right now. ({type(e).__name__})"


if __name__ == "__main__":
    test_response = ask("Hello! Can you help me find a house in Colombo?")
    print("Test Response:\n", test_response)
