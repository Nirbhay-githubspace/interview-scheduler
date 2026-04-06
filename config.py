"""
Configuration module

Loads configuration from environment variables with sensible defaults.
Supports both local (.env) and Streamlit Cloud (secrets).
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load local .env (works locally only)
load_dotenv()

# 🔥 ADD THIS BLOCK (CRITICAL FOR STREAMLIT CLOUD)
try:
    import streamlit as st
    if "GOOGLE_API_KEY" in st.secrets:
        os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
except Exception:
    # Streamlit not available (local CLI run)
    pass


class Config:
    """Application configuration"""

    # Google Gemini API
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')

    # Google Calendar API (Optional)
    GOOGLE_CALENDAR_CREDENTIALS_PATH = os.getenv(
        'GOOGLE_CALENDAR_CREDENTIALS_PATH',
        'credentials.json'
    )
    GOOGLE_CALENDAR_TOKEN_PATH = os.getenv(
        'GOOGLE_CALENDAR_TOKEN_PATH',
        'token.pickle'
    )

    # Email Configuration (Optional)
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USER = os.getenv('SMTP_USER', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')

    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./recruitment.db')

    # Application
    APP_HOST = os.getenv('APP_HOST', '0.0.0.0')
    APP_PORT = int(os.getenv('APP_PORT', '8000'))
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Storage
    RESUME_STORAGE_PATH = os.getenv('RESUME_STORAGE_PATH', './data/uploaded_resumes')
    OUTPUT_STORAGE_PATH = os.getenv('OUTPUT_STORAGE_PATH', './data/outputs')

    # Agent Configuration
    SKILLS_MATCH_THRESHOLD = float(os.getenv('SKILLS_MATCH_THRESHOLD', '70'))
    CULTURAL_FIT_THRESHOLD = float(os.getenv('CULTURAL_FIT_THRESHOLD', '65'))
    SKILLS_WEIGHT = float(os.getenv('SKILLS_WEIGHT', '0.6'))
    CULTURAL_FIT_WEIGHT = float(os.getenv('CULTURAL_FIT_WEIGHT', '0.3'))
    EXPERIENCE_WEIGHT = float(os.getenv('EXPERIENCE_WEIGHT', '0.1'))

    # Model Configuration
    DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'gemini-2.0-flash-exp')

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        errors = []

        if not cls.GOOGLE_API_KEY:
            errors.append(
                "GOOGLE_API_KEY is required. Set it in Streamlit secrets or .env file."
            )

        if not cls.SECRET_KEY or cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            if not cls.DEBUG:
                errors.append(
                    "SECRET_KEY must be set in production."
                )

        if errors:
            raise ValueError(
                "Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors)
            )

        return True


# Create global config instance
config = Config()