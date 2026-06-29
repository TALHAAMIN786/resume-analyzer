import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_secret(key: str, default: str = "") -> str:
    """Read from Streamlit Cloud secrets first, fall back to .env for local dev."""
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key, default)

# ── API Config ─────────────────────────────────────────────────────────────────
GEMINI_API_KEY     = get_secret("GEMINI_API_KEY")
GEMINI_MODEL       = "gemini-2.5-flash"
MAX_TOKENS         = 2000

# ── File Config ────────────────────────────────────────────────────────────────
ALLOWED_EXTENSIONS = ["pdf", "docx"]
MAX_FILE_SIZE_MB   = 5
UPLOAD_DIR         = "uploads"

# ── Score Thresholds ───────────────────────────────────────────────────────────
SCORE_EXCELLENT    = 80
SCORE_GOOD         = 60
SCORE_POOR         = 40

# ── App Labels ─────────────────────────────────────────────────────────────────
APP_TITLE          = "🎯 AI Resume Analyzer"
APP_SUBTITLE       = "Powered by Gemini AI · Get your ATS score in seconds"
SIDEBAR_TITLE      = "📂 Upload Your Resume"

# ── Validate ───────────────────────────────────────────────────────────────────
def validate_config():
    if not GEMINI_API_KEY:
        return False, "❌ GEMINI_API_KEY is missing. Add it to your .env file or Streamlit secrets."
    if GEMINI_API_KEY == "your_api_key_here":
        return False, "❌ Replace 'your_api_key_here' with your real API key."
    return True, "✅ Config loaded successfully."

if __name__ == "__main__":
    ok, msg = validate_config()
    print(msg)
    if ok:
        print(f"  Model  : {GEMINI_MODEL}")
        print(f"  Tokens : {MAX_TOKENS}")
        print(f"  Upload : {UPLOAD_DIR}/")