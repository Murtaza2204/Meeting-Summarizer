import os
from dotenv import load_dotenv

load_dotenv()

# API Keys and Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AZURE_API_KEY = os.getenv("AZURE_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")
SARVAM_LANGUAGE_CODE = os.getenv("SARVAM_LANGUAGE_CODE", "")
SARVAM_MODEL = os.getenv("SARVAM_MODEL", "saaras:v3")
SARVAM_TRANSCRIPTION_MODE = os.getenv("SARVAM_TRANSCRIPTION_MODE", "translate")

# Flask Configuration
FLASK_ENV = os.getenv("FLASK_ENV", "development")
DEBUG = FLASK_ENV == "development"

# Upload Configuration
UPLOAD_FOLDER = "uploads"
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
