"""
Courses controller — HTTP handlers for course, enrolment, and member endpoints.
All data-access logic lives in models.course and models.user.
"""
from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from models import course as course_model
from models import user as user_model

courses_bp = Blueprint("courses", __name__)


def _role() -> str:
    return get_jwt().get("role", "")


# ── List / Create courses ────────────────────────────────────────────────────


@courses_bp.route("/courses", methods=["GET"])
def get_all_courses():
    """Public: list every course."""
    return jsonify(course_model.get_all()), 200


@courses_bp.route("/courses/<course_id>", methods=["GET"])
@jwt_required()
def get_course(course_id: str):
    course = course_model.get_by_id(course_id)
    if not course:
        return jsonify({"error": "Course not found"}), 404
    return jsonify(course), 200


@courses_bp.route("/courses", methods=["POST"])
@jwt_required()
def create_course():
    """Admin only: create a new course."""
    if _role() != "Admin":
        return jsonify({"error": "Admin access required"}), 403

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    course_id   = (data.get("course_id") or "").strip()
    title       = (data.get("title") or "").strip()
    code        = (data.get("code") or "").strip()
    description = (data.get("description") or "")
    lec_id      = (data.get("lec_id") or "").strip() or None

    if not all([course_id, title, code]):
        return jsonify({"error": "course_id, title, and code are required"}), 400

    if course_model.id_or_code_taken(course_id, code):
        return jsonify({"error": "Course ID or code already exists"}), 409

    # If a lecturer is specified, verify they exist before inserting.
    if lec_id and not user_model.find_by_id_and_type(lec_id, "Lecturer"):
        return jsonify({"error": "Lecturer not found"}), 404

    course = course_model.create(course_id, title, code, description, lec_id)
    return jsonify(course), 201


# ── Student / Lecturer course views ─────────────────────────────────────────


@courses_bp.route("/students/<student_id>/courses", methods=["GET"])
@jwt_required()
def get_student_courses(student_id: str):
    # Students may only view their own course list; Lecturers and Admins may view any.
    caller = get_jwt_identity()
    role   = _role()
    if role not in ("Admin", "Lecturer") and caller != student_id:
        return jsonify({"error": "You may only view your own course list"}), 403
    return jsonify(course_model.get_for_student(student_id)), 200


@courses_bp.route("/lecturers/<lecturer_id>/courses", methods=["GET"])
@jwt_required()
def get_lecturer_courses(lecturer_id: str):
    # Lecturers may only view their own list; Admins may view any lecturer's list.
    caller = get_jwt_identity()
    role   = _role()
    if role != "Admin" and caller != lecturer_id:
        return jsonify({"error": "You may only view your own course list"}), 403
    return jsonify(course_model.get_for_lecturer(lecturer_id)), 200


# ── Enrolment ────────────────────────────────────────────────────────────────


@courses_bp.route("/courses/<course_id>/enroll", methods=["POST"])
@jwt_required()
def enroll_student(course_id: str):
    role    = _role()
    caller  = get_jwt_identity()
    data    = request.get_json(silent=True) or {}

    if role == "Student":
        student_id = caller
    elif role == "Admin":
        student_id = (data.get("student_id") or "").strip()
        if not student_id:
            return jsonify({"error": "student_id required"}), 400
    else:
        return jsonify({"error": "Only students or admins can enrol"}), 403

    if not course_model.get_by_id(course_id):
        return jsonify({"error": "Course not found"}), 404

    if not user_model.find_by_id_and_type(student_id, "Student"):
        return jsonify({"error": "Student not found"}), 404

    if course_model.is_enrolled(student_id, course_id):
        return jsonify({"error": "Student already enrolled in this course"}), 409

    # Spec constraint: a student may not enroll in more than 6 courses.
    if course_model.enrollment_count(student_id) >= 6:
        return jsonify({"error": "Students may not enroll in more than 6 courses"}), 400

    course_model.enroll(student_id, course_id)
    return jsonify({"message": f"Student {student_id} enrolled in {course_id}"}), 201


@courses_bp.route("/courses/<course_id>/assign-lecturer", methods=["POST"])
@jwt_required()
def assign_lecturer(course_id: str):
    """Admin only: assign a lecturer to a course."""
    if _role() != "Admin":
        return jsonify({"error": "Admin access required"}), 403

    data   = request.get_json(silent=True) or {}
    lec_id = (data.get("lec_id") or "").strip()
    if not lec_id:
        return jsonify({"error": "lec_id is required"}), 400

    if not course_model.get_by_id(course_id):
        return jsonify({"error": "Course not found"}), 404

    if not user_model.find_by_id_and_type(lec_id, "Lecturer"):
        return jsonify({"error": "Lecturer not found"}), 404

    if course_model.lecturer_course_count(lec_id) >= 5:
        return jsonify({"error": "Lecturer already teaches the maximum of 5 courses"}), 400

    course_model.assign_lecturer(course_id, lec_id)
    return jsonify({"message": f"Lecturer {lec_id} assigned to {course_id}"}), 200


@courses_bp.route("/courses/<course_id>/members", methods=["GET"])
@jwt_required()
def get_course_members(course_id: str):
    # Sensitive — exposes student emails. Restrict to Lecturer and Admin only.
    if _role() not in ("Lecturer", "Admin"):
        return jsonify({"error": "Only lecturers and admins can view the course member list"}), 403

    members = course_model.get_members(course_id)
    if members is None:
        return jsonify({"error": "Course not found"}), 404

    return jsonify(members), 200
