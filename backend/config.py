import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """ Basic configuration class for the Flask application. """
    DEBUG = True
    DATABASE_URL = str = os.environ.get(
        'DATABASE_URL',
        '').replace('postgres://', 'postgresql://')
    JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY",)
    # Token valid for 24 hours
    JWT_ACCESS_TOKEN_EXPIRES: int = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", 86400))
    DEBUG: bool = os.environ.get("FLASK_ENV", "production") == "development"
