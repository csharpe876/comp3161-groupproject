"""
User model — all database operations for the Users table.
"""
from __future__ import annotations

from db import execute_returning, query_one


def find_by_identifier(identifier: str) -> dict | None:
    """Return a full user row (including password) by UserID or Email."""
    return query_one(
        "SELECT UserID, Password, Name, Email, AccountType "
        "FROM Users WHERE UserID = %s OR Email = %s",
        (identifier, identifier),
    )


def find_duplicate(user_id: str, email: str) -> dict | None:
    """Return a row if the given UserID or Email is already taken."""
    return query_one(
        "SELECT UserID FROM Users WHERE UserID = %s OR Email = %s",
        (user_id, email),
    )


def find_by_id_and_type(user_id: str, account_type: str) -> dict | None:
    """Return a user row only if the UserID exists and the AccountType matches."""
    return query_one(
        "SELECT UserID FROM Users WHERE UserID = %s AND AccountType = %s",
        (user_id, account_type),
    )


def create(
    user_id: str,
    hashed_password: str,
    name: str,
    email: str,
    account_type: str,
) -> dict | None:
    """Insert a new user and return the created row (without the password)."""
    return execute_returning(
        """INSERT INTO Users (UserID, Password, Name, Email, AccountType)
           VALUES (%s, %s, %s, %s, %s)
           RETURNING UserID, Name, Email, AccountType, CreatedAt""",
        (user_id, hashed_password, name, email, account_type),
    )
