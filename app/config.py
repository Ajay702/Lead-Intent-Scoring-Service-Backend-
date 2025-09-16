import os
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///instance/app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    # Create tables automatically on startup when migrations are not used
    AUTO_CREATE_DB = os.getenv("AUTO_CREATE_DB", "true").lower() in {"1", "true", "yes"}
