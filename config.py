"""
Application Configuration
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key-change-in-production")
    DATABASE = "calories.db"
    TIMEZONE = "Asia/Kolkata"
    
    # Google OAuth Configuration
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:5000/auth/google/callback")
    GOOGLE_AUTH_URI = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URI = "https://oauth2.googleapis.com/token"
    GOOGLE_USERINFO_URI = "https://openidconnect.googleapis.com/v1/userinfo"
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = "gpt-3.5-turbo"
    OPENAI_MAX_TOKENS = 20
    OPENAI_TEMPERATURE = 0

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    DATABASE = ":memory:"

# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig
}

def get_config(env=None):
    """Get configuration based on environment"""
    if env is None:
        env = os.getenv("FLASK_ENV", "development")
    return config.get(env, DevelopmentConfig)
