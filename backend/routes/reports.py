"""
Reports controller — HTTP handlers for the five Admin report views.
All data-access logic lives in models.report.
"""
from __future__ import annotations

from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt, jwt_required

from models import report as report_model

api = Blueprint("reports", __name__)


def _require_staff():
    """Return a 403 response if the caller is not an Admin or Lecturer, else None."""
    if get_jwt().get("role", "") not in ("Admin", "Lecturer"):
        return jsonify({"error": "Admin or Lecturer access required"}), 403
    return None


@api.route("/courses-50plus", methods=["GET"])
@jwt_required()
def courses_50plus():
    """All courses with 50 or more enrolled students."""
    err = _require_staff()
    if err:
        return err
    return jsonify(report_model.courses_50plus()), 200


@api.route("/students-5plus", methods=["GET"])
@jwt_required()
def students_5plus():
    """All students enrolled in 5 or more courses."""
    err = _require_staff()
    if err:
        return err
    return jsonify(report_model.students_5plus()), 200


@api.route("/lecturers-3plus", methods=["GET"])
@jwt_required()
def lecturers_3plus():
    """All lecturers who teach 3 or more courses."""
    err = _require_staff()
    if err:
        return err
    return jsonify(report_model.lecturers_3plus()), 200


@api.route("/top10-enrolled", methods=["GET"])
@jwt_required()
def top10_enrolled():
    """The 10 most enrolled courses."""
    err = _require_staff()
    if err:
        return err
    return jsonify(report_model.top10_enrolled()), 200


@api.route("/top10-averages", methods=["GET"])
@jwt_required()
def top10_averages():
    """Top 10 students by overall grade average."""
    err = _require_staff()
    if err:
        return err
    return jsonify(report_model.top10_averages()), 200
