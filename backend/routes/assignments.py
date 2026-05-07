"""
Assignments controller — HTTP handlers for assignments, submissions, and grading.
All data-access logic lives in models.assignment, models.course, and models.user.
"""
from __future__ import annotations

from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from models import assignment as assignment_model
from models import course as course_model
from models import user as user_model

assignments_bp = Blueprint("assignments", __name__)


# ── Assignments ───────────────────────────────────────────────────────────────


@assignments_bp.route("/courses/<course_id>/assignments", methods=["GET"])
@jwt_required()
def get_course_assignments(course_id: str):
    if not course_model.get_by_id(course_id):
        return jsonify({"error": "Course not found"}), 404
    return jsonify(assignment_model.get_all_for_course(course_id)), 200


@assignments_bp.route("/courses/<course_id>/assignments", methods=["POST"])
@jwt_required()
def create_assignment(course_id: str):
    role = get_jwt().get("role", "")
    if role not in ("Lecturer", "Admin"):
        return jsonify({"error": "Only lecturers and admins can create assignments"}), 403

    course = course_model.get_by_id(course_id)
    if not course:
        return jsonify({"error": "Course not found"}), 404

    # Lecturers may only create assignments for courses they teach.
    if role == "Lecturer" and course["lecid"] != get_jwt_identity():
        return jsonify({"error": "You do not teach this course and cannot create assignments for it"}), 403

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    title       = (data.get("title") or "").strip()
    description = data.get("description") or ""
    due_date    = data.get("due_date")

    try:
        max_grade = float(data.get("max_grade", 100))
    except (TypeError, ValueError):
        return jsonify({"error": "max_grade must be a number"}), 400

    if not title:
        return jsonify({"error": "title is required"}), 400
    if max_grade <= 0:
        return jsonify({"error": "max_grade must be greater than 0"}), 400

    # Validate due_date format if provided.
    if due_date:
        parsed = False
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d"):
            try:
                datetime.strptime(due_date, fmt)
                parsed = True
                break
            except ValueError:
                pass
        if not parsed:
            return jsonify({"error": "due_date must be ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"}), 400

    assignment = assignment_model.create(course_id, title, description, due_date, max_grade)
    return jsonify(assignment), 201


# ── Submissions ───────────────────────────────────────────────────────────────


@assignments_bp.route("/assignments/<int:assignment_id>/submit", methods=["POST"])
@jwt_required()
def submit_assignment(assignment_id: int):
    role = get_jwt().get("role", "")
    if role != "Student":
        return jsonify({"error": "Only students can submit assignments"}), 403

    assignment = assignment_model.get_by_id(assignment_id)
    if not assignment:
        return jsonify({"error": "Assignment not found"}), 404

    student_id = get_jwt_identity()

    # Verify the student is enrolled in the course this assignment belongs to.
    if not course_model.is_enrolled(student_id, assignment["courseid"]):
        return jsonify({"error": "You are not enrolled in the course this assignment belongs to"}), 403

    if assignment_model.submission_exists(assignment_id, student_id):
        return jsonify({"error": "You have already submitted this assignment"}), 409

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    content = (data.get("content") or "").strip()
    if not content:
        return jsonify({"error": "content is required"}), 400

    submission = assignment_model.create_submission(assignment_id, student_id, content)
    return jsonify(submission), 201


@assignments_bp.route("/assignments/<int:assignment_id>/submissions", methods=["GET"])
@jwt_required()
def get_submissions(assignment_id: int):
    """
    Lecturers/Admins see all submissions.
    Students see only their own submission.
    """
    role   = get_jwt().get("role", "")
    caller = get_jwt_identity()

    if not assignment_model.get_by_id(assignment_id):
        return jsonify({"error": "Assignment not found"}), 404

    if role in ("Lecturer", "Admin"):
        submissions = assignment_model.get_all_submissions(assignment_id)
    else:
        submissions = assignment_model.get_student_submissions(assignment_id, caller)

    return jsonify(submissions), 200


# ── Grading ───────────────────────────────────────────────────────────────────


@assignments_bp.route("/submissions/<int:submission_id>/grade", methods=["POST"])
@jwt_required()
def grade_submission(submission_id: int):
    role = get_jwt().get("role", "")
    if role not in ("Lecturer", "Admin"):
        return jsonify({"error": "Only lecturers and admins can grade submissions"}), 403

    submission = assignment_model.get_submission_for_grading(submission_id)
    if not submission:
        return jsonify({"error": "Submission not found"}), 404

    # Lecturers may only grade submissions from courses they teach.
    if role == "Lecturer" and submission["lecid"] != get_jwt_identity():
        return jsonify({"error": "You do not teach the course this submission belongs to"}), 403

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    if "grade" not in data:
        return jsonify({"error": "grade is required"}), 400

    try:
        grade = float(data["grade"])
    except (TypeError, ValueError):
        return jsonify({"error": "grade must be a number"}), 400

    if grade < 0 or grade > float(submission["maxgrade"]):
        return jsonify({
            "error": f"grade must be between 0 and {submission['maxgrade']}"
        }), 400

    result = assignment_model.upsert_grade(submission_id, grade, get_jwt_identity())
    return jsonify(result), 200


@assignments_bp.route("/students/<student_id>/average", methods=["GET"])
@jwt_required()
def get_student_average(student_id: str):
    """Return the overall grade average (as a percentage) for a student."""
    caller = get_jwt_identity()
    role   = get_jwt().get("role", "")
    if role not in ("Admin", "Lecturer") and caller != student_id:
        return jsonify({"error": "You may only view your own grade average"}), 403

    if not user_model.find_by_id_and_type(student_id, "Student"):
        return jsonify({"error": "Student not found"}), 404

    average = assignment_model.get_student_average(student_id)
    return jsonify({"student_id": student_id, "overall_average": average}), 200
