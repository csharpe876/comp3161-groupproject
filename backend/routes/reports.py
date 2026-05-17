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


# ── Ad-hoc stats ─────────────────────────────────────────────────────────────

@api.route("/stats/total-students", methods=["GET"])
@jwt_required()
def total_students():
    err = _require_staff()
    if err:
        return err
    return jsonify(report_model.total_students()), 200


@api.route("/stats/total-lecturers", methods=["GET"])
@jwt_required()
def total_lecturers():
    err = _require_staff()
    if err:
        return err
    return jsonify(report_model.total_lecturers()), 200


@api.route("/stats/total-courses", methods=["GET"])
@jwt_required()
def total_courses():
    err = _require_staff()
    if err:
        return err
    return jsonify(report_model.total_courses()), 200


@api.route("/stats/enrollment-per-course", methods=["GET"])
@jwt_required()
def enrollment_per_course():
    err = _require_staff()
    if err:
        return err
    return jsonify(report_model.enrollment_per_course()), 200


@api.route("/stats/courses-per-lecturer", methods=["GET"])
@jwt_required()
def courses_per_lecturer():
    err = _require_staff()
    if err:
        return err
    return jsonify(report_model.courses_per_lecturer()), 200


@api.route("/stats/students-lt3-courses", methods=["GET"])
@jwt_required()
def students_lt3_courses():
    err = _require_staff()
    if err:
        return err
    return jsonify(report_model.students_lt3_courses()), 200


@api.route("/stats/lecturers-no-courses", methods=["GET"])
@jwt_required()
def lecturers_no_courses():
    err = _require_staff()
    if err:
        return err
    return jsonify(report_model.lecturers_no_courses()), 200
