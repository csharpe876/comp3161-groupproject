"""
Authentication controller: register and login.
Passwords for API-registered users are hashed with bcrypt.
Seeded test users (from insertdata.py) use SHA-256; the login endpoint
falls back to SHA-256 verification so both work.
"""
from __future__ import annotations

import hashlib

import bcrypt
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    verify_jwt_in_request,
)

from models import user as user_model

api = Blueprint("auth", __name__)


@api.route("/register", methods=["POST"])
def register():
    # Optionally read a JWT so that Admin-account creation can be gated.
    # The endpoint remains fully public for Student/Lecturer self-registration.
    verify_jwt_in_request(optional=True)

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    user_id      = (data.get("userid") or "").strip()
    password     = (data.get("password") or "").strip()
    name         = (data.get("name") or "").strip()
    email        = (data.get("email") or "").strip()
    account_type = (data.get("account_type") or "Student").strip()

    # ── Required field validation ──────────────────────────────────────────
    missing = [f for f, v in [("userid", user_id), ("password", password),
                               ("name", name), ("email", email)] if not v]
    if missing:
        return jsonify({"error": f"Required fields missing: {', '.join(missing)}"}), 400

    if account_type not in ("Admin", "Lecturer", "Student"):
        return jsonify({"error": "account_type must be Admin, Lecturer, or Student"}), 400

    # ── Admin-account guard ────────────────────────────────────────────────
    # Only an already-authenticated Admin may register a new Admin account.
    if account_type == "Admin":
        caller_role = get_jwt().get("role", "") if get_jwt() else ""
        if caller_role != "Admin":
            return jsonify({
                "error": "Only an existing Admin can register an Admin account. "
                         "Authenticate as an Admin and include your Bearer token."
            }), 403

    # ── Password strength ─────────────────────────────────────────────────
    if len(password) < 6:
        return jsonify({"error": "password must be at least 6 characters long"}), 400

    # ── Basic email format check ──────────────────────────────────────────
    if "@" not in email or "." not in email.split("@")[-1]:
        return jsonify({"error": "A valid email address is required"}), 400

    # ── Uniqueness check (delegated to model) ─────────────────────────────
    if user_model.find_duplicate(user_id, email):
        return jsonify({"error": "A user with that ID or email already exists"}), 409

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user = user_model.create(user_id, hashed, name, email, account_type)
    return jsonify({"message": "User registered successfully", "user": user}), 201


@api.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    identifier = (data.get("userid") or data.get("email") or "").strip()
    password   = (data.get("password") or "").strip()

    if not identifier:
        return jsonify({"error": "userid or email is required"}), 400
    if not password:
        return jsonify({"error": "password is required"}), 400

    user = user_model.find_by_identifier(identifier)

    # Constant-time failure path to prevent timing attacks
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
