"""
Flask application factory.
"""
from __future__ import annotations

import decimal
from datetime import date, datetime, time

import os

from flask import Flask, jsonify
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import Config
from db import init_pool


class _AppJSONProvider(DefaultJSONProvider):
    """Extend default provider to serialise Decimal + date/time types."""

    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        if isinstance(obj, (datetime, date, time)):
            return obj.isoformat()
        return super().default(obj)


def create_app() -> Flask:
    app = Flask(__name__)

    # JSON provider that handles Decimal / date types from psycopg2
    app.json_provider_class = _AppJSONProvider
    app.json = _AppJSONProvider(app)

    app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = Config.JWT_ACCESS_TOKEN_EXPIRES
    app.config["DEBUG"] = Config.DEBUG

    # In production set ALLOWED_ORIGINS to the exact front-end origin,
    # e.g. "https://yourdomain.com". Defaults to "*" only for local dev.
    _allowed = os.environ.get("ALLOWED_ORIGINS", "*").split(",")
    CORS(app, resources={r"/api/*": {"origins": _allowed}})
    JWTManager(app)

    # Initialise DB connection pool
    init_pool()

    # ── Blueprints ──────────────────────────────────────────────────────────
    from routes.auth import api as auth_api
    from routes.courses import api as courses_api
    from routes.calendar import api as calendar_api
    from routes.forums import api as forums_api
    from routes.content import api as content_api
    from routes.assignments import api as assignments_api
    from routes.reports import api as reports_api

    app.register_blueprint(auth_api,        url_prefix="/api/auth")
    app.register_blueprint(courses_api,     url_prefix="/api")
    app.register_blueprint(calendar_api,    url_prefix="/api")
    app.register_blueprint(forums_api,      url_prefix="/api")
    app.register_blueprint(content_api,     url_prefix="/api")
    app.register_blueprint(assignments_api, url_prefix="/api")
    app.register_blueprint(reports_api,     url_prefix="/api/reports")

    # ── Health check ────────────────────────────────────────────────────────
    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"})

    # ── Error handlers ──────────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    return app

if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=5000)
