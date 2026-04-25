"""
Report routes — each endpoint queries one of the five materialised views.
"""
from __future__ import annotations

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from db import query_all

reports_bp = Blueprint("reports", __name__)


@reports_bp.get("/courses-50plus")
@jwt_required()
def courses_50plus():
    """All courses with 50 or more enrolled students."""
    return jsonify(query_all("SELECT * FROM v_courses_50plus_students")), 200


@reports_bp.get("/students-5plus")
@jwt_required()
def students_5plus():
    """All students enrolled in 5 or more courses."""
    return jsonify(query_all("SELECT * FROM v_students_5plus_courses")), 200


@reports_bp.get("/lecturers-3plus")
@jwt_required()
def lecturers_3plus():
    """All lecturers who teach 3 or more courses."""
    return jsonify(query_all("SELECT * FROM v_lecturers_3plus_courses")), 200


@reports_bp.get("/top10-enrolled")
@jwt_required()
def top10_enrolled():
    """The 10 most enrolled courses."""
    return jsonify(query_all("SELECT * FROM v_top10_most_enrolled")), 200


@reports_bp.get("/top10-averages")
@jwt_required()
def top10_averages():
    """Top 10 students by overall grade average."""
    return jsonify(query_all("SELECT * FROM v_top10_student_averages")), 200
