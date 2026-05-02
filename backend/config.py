import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """ Basic configuration class for the Flask application. """
    DATABASE_URL: str = os.environ.get(
        'DATABASE_URL',
        '').replace('postgres://', 'postgresql://')

    _jwt_secret = os.environ.get("JWT_SECRET_KEY")
    if not _jwt_secret:
        raise RuntimeError(
            "JWT_SECRET_KEY environment variable is not set. "
            "Set it to a long random string before starting the server."
        )
    JWT_SECRET_KEY: str = _jwt_secret

    # Token valid for 24 hours by default; override with JWT_ACCESS_TOKEN_EXPIRES env var
    JWT_ACCESS_TOKEN_EXPIRES: int = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", 86400))
    DEBUG: bool = os.environ.get("FLASK_ENV", "production") == "development"
