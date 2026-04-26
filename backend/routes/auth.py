"""
Authentication routes: register and login.
Passwords for API-registered users are hashed with bcrypt.
Seeded test users (from insertdata.py) use SHA-256; the login endpoint
falls back to SHA-256 verification so both work.
"""
from __future__ import annotations

import hashlib

import bcrypt
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

from db import execute_returning, query_one

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    user_id     = (data.get("userid") or "").strip()
    password    = (data.get("password") or "").strip()
    name        = (data.get("name") or "").strip()
    email       = (data.get("email") or "").strip()
    account_type = (data.get("account_type") or "Student").strip()

    if not all([user_id, password, name, email]):
        return jsonify({"error": "userid, password, name, and email are required"}), 400

    if account_type not in ("Admin", "Lecturer", "Student"):
        return jsonify({"error": "account_type must be Admin, Lecturer, or Student"}), 400

    if len(password) < 6:
        return jsonify({"error": "password must be at least 6 characters"}), 400

    # Reject if user ID or email already taken
    existing = query_one(
        "SELECT UserID FROM Users WHERE UserID = %s OR Email = %s",
        (user_id, email),
    )
    if existing:
        return jsonify({"error": "A user with that ID or email already exists"}), 409

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    user = execute_returning(
        """INSERT INTO Users (UserID, Password, Name, Email, AccountType)
           VALUES (%s, %s, %s, %s, %s)
           RETURNING UserID, Name, Email, AccountType, CreatedAt""",
        (user_id, hashed, name, email, account_type),
    )
    return jsonify({"message": "User registered successfully", "user": user}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    identifier = (data.get("userid") or data.get("email") or "").strip()
    password   = (data.get("password") or "").strip()

    if not identifier or not password:
        return jsonify({"error": "userid (or email) and password are required"}), 400

    user = query_one(
        "SELECT UserID, Password, Name, Email, AccountType FROM Users WHERE UserID = %s OR Email = %s",
        (identifier, identifier),
    )

    # Use a constant-time failure path to prevent timing attacks
    if not user:
        bcrypt.checkpw(b"dummy", bcrypt.hashpw(b"guard", bcrypt.gensalt()))
        return jsonify({"error": "Invalid credentials"}), 401

    stored = user["password"]
    matched = False

    # Bcrypt path (API-registered users)
    if stored.startswith("$2b$") or stored.startswith("$2a$"):
        try:
            matched = bcrypt.checkpw(password.encode(), stored.encode())
        except Exception:
            matched = False
    else:
        # SHA-256 fallback for seeded data
        matched = hashlib.sha256(password.encode()).hexdigest() == stored

    if not matched:
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(
        identity=user["userid"],
        additional_claims={"role": user["accounttype"], "name": user["name"]},
    )

    return jsonify({
        "token": token,
        "user": {
            "userid":       user["userid"],
            "name":         user["name"],
            "email":        user["email"],
            "account_type": user["accounttype"],
        },
    }), 200
