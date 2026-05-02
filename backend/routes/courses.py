"""
Course, enrolment, and member routes.
"""
from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from db import execute, execute_returning, query_one, query_all

courses_bp = Blueprint("courses", __name__)


def _role() -> str:
    return get_jwt().get("role", "")


# ── List / Create courses ────────────────────────────────────────────────────


@courses_bp.route("/courses", methods=["GET"])
def get_all_courses():
    """Public: list every course."""
    courses = query_all(
        """SELECT c.CourseID, c.CourseTitle, c.CourseCode, c.Description,
                  c.LecID, u.Name AS LecturerName, c.CreatedAt,
                  COUNT(e.UserID) AS EnrolledCount
           FROM Courses c
           LEFT JOIN Users u    ON c.LecID    = u.UserID
           LEFT JOIN Enrolled e ON c.CourseID = e.CourseID
           GROUP BY c.CourseID, c.CourseTitle, c.CourseCode,
                    c.Description, c.LecID, u.Name, c.CreatedAt
           ORDER BY c.CourseID"""
    )
    return jsonify(courses), 200


@courses_bp.route("/courses/<course_id>", methods=["GET"])
@jwt_required()
def get_course(course_id: str):
    course = query_one(
        """SELECT c.CourseID, c.CourseTitle, c.CourseCode, c.Description,
                  c.LecID, u.Name AS LecturerName, c.CreatedAt
           FROM Courses c
           LEFT JOIN Users u ON c.LecID = u.UserID
           WHERE c.CourseID = %s""",
        (course_id,),
    )
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

    if query_one(
        "SELECT CourseID FROM Courses WHERE CourseID = %s OR CourseCode = %s",
        (course_id, code),
    ):
        return jsonify({"error": "Course ID or code already exists"}), 409

    # If a lecturer is specified, verify they exist before inserting.
    if lec_id and not query_one(
        "SELECT UserID FROM Users WHERE UserID = %s AND AccountType = 'Lecturer'",
        (lec_id,),
    ):
        return jsonify({"error": "Lecturer not found"}), 404

    course = execute_returning(
        """INSERT INTO Courses (CourseID, CourseTitle, CourseCode, Description, LecID)
           VALUES (%s, %s, %s, %s, %s)
           RETURNING CourseID, CourseTitle, CourseCode, Description, LecID, CreatedAt""",
        (course_id, title, code, description, lec_id),
    )
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

    courses = query_all(
        """SELECT c.CourseID, c.CourseTitle, c.CourseCode, c.Description,
                  c.LecID, u.Name AS LecturerName, e.EnrolledAt
           FROM Courses c
           JOIN Enrolled e ON c.CourseID = e.CourseID
           LEFT JOIN Users u ON c.LecID = u.UserID
           WHERE e.UserID = %s
           ORDER BY c.CourseID""",
        (student_id,),
    )
    return jsonify(courses), 200


@courses_bp.route("/lecturers/<lecturer_id>/courses", methods=["GET"])
@jwt_required()
def get_lecturer_courses(lecturer_id: str):
    # Lecturers may only view their own list; Admins may view any lecturer's list.
    # Students have no access.
    caller = get_jwt_identity()
    role   = _role()
    if role != "Admin" and caller != lecturer_id:
        return jsonify({"error": "You may only view your own course list"}), 403

    courses = query_all(
        """SELECT c.CourseID, c.CourseTitle, c.CourseCode, c.Description,
                  c.CreatedAt, COUNT(e.UserID) AS EnrolledCount
           FROM Courses c
           LEFT JOIN Enrolled e ON c.CourseID = e.CourseID
           WHERE c.LecID = %s
           GROUP BY c.CourseID, c.CourseTitle, c.CourseCode, c.Description, c.CreatedAt
           ORDER BY c.CourseID""",
        (lecturer_id,),
    )
    return jsonify(courses), 200


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

    if not query_one("SELECT CourseID FROM Courses WHERE CourseID = %s", (course_id,)):
        return jsonify({"error": "Course not found"}), 404

    if not query_one(
        "SELECT UserID FROM Users WHERE UserID = %s AND AccountType = 'Student'",
        (student_id,),
    ):
        return jsonify({"error": "Student not found"}), 404

    if query_one(
        "SELECT 1 FROM Enrolled WHERE UserID = %s AND CourseID = %s",
        (student_id, course_id),
    ):
        return jsonify({"error": "Student already enrolled in this course"}), 409

    # Spec constraint: a student may not enroll in more than 6 courses.
    count_row = query_one(
        "SELECT COUNT(*) AS cnt FROM Enrolled WHERE UserID = %s", (student_id,)
    )
    if count_row and int(count_row["cnt"]) >= 6:
        return jsonify({"error": "Students may not enroll in more than 6 courses"}), 400

    execute(
        "INSERT INTO Enrolled (UserID, CourseID) VALUES (%s, %s)",
        (student_id, course_id),
    )
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

    if not query_one("SELECT CourseID FROM Courses WHERE CourseID = %s", (course_id,)):
        return jsonify({"error": "Course not found"}), 404

    if not query_one(
        "SELECT UserID FROM Users WHERE UserID = %s AND AccountType = 'Lecturer'",
        (lec_id,),
    ):
        return jsonify({"error": "Lecturer not found"}), 404

    count_row = query_one(
        "SELECT COUNT(*) AS cnt FROM Courses WHERE LecID = %s", (lec_id,)
    )
    if count_row and int(count_row["cnt"]) >= 5:
        return jsonify({"error": "Lecturer already teaches the maximum of 5 courses"}), 400

    execute("UPDATE Courses SET LecID = %s WHERE CourseID = %s", (lec_id, course_id))
    return jsonify({"message": f"Lecturer {lec_id} assigned to {course_id}"}), 200


# ── Members ──────────────────────────────────────────────────────────────────


@courses_bp.route("/courses/<course_id>/members", methods=["GET"])
@jwt_required()
def get_course_members(course_id: str):
    # Sensitive — exposes student emails. Restrict to Lecturer and Admin only.
    if _role() not in ("Lecturer", "Admin"):
        return jsonify({"error": "Only lecturers and admins can view the course member list"}), 403

    course = query_one(
        """SELECT c.CourseID, c.CourseTitle, c.LecID,
                  u.Name AS LecturerName, u.Email AS LecturerEmail
           FROM Courses c
           LEFT JOIN Users u ON c.LecID = u.UserID
           WHERE c.CourseID = %s""",
        (course_id,),
    )
    if not course:
        return jsonify({"error": "Course not found"}), 404

    students = query_all(
        """SELECT u.UserID, u.Name, u.Email, e.EnrolledAt
           FROM Users u
           JOIN Enrolled e ON u.UserID = e.UserID
           WHERE e.CourseID = %s
           ORDER BY u.Name""",
        (course_id,),
    )

    return jsonify({
        "course_id":    course["courseid"],
        "course_title": course["coursetitle"],
        "lecturer": {
            "userid": course["lecid"],
            "name":   course["lecturername"],
            "email":  course["lectureremail"],
        } if course["lecid"] else None,
        "students":      students,
        "total_members": len(students) + (1 if course["lecid"] else 0),
    }), 200
