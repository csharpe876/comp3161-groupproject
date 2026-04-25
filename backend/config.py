import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DATABASE_URL: str = os.environ.get(
        "DATABASE_URL",
        "postgresql://courseuser:coursepassword@localhost:5432/coursedb",
    )
    JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY", "dev-secret-change-in-production")
    # Token valid for 24 hours
    JWT_ACCESS_TOKEN_EXPIRES: int = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", 86400))
    DEBUG: bool = os.environ.get("FLASK_ENV", "production") == "development"
