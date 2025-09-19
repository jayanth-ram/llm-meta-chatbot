import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
MODE = os.getenv("MODE", "fallback")
CORS_ORIGIN = os.getenv("CORS_ORIGIN", "http://localhost:5173")
TIMEOUT_SECS = int(os.getenv("TIMEOUT_SECS", "20"))
PORT = int(os.getenv("PORT", "8000"))
