"""
Assignment, submission, and grading routes.
Each grade a student receives contributes to their overall average percentage.
"""
from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from db import execute_returning, query_all, query_one

assignments_bp = Blueprint("assignments", __name__)


# ── Assignments ───────────────────────────────────────────────────────────────


@assignments_bp.get("/courses/<course_id>/assignments")
@jwt_required()
def get_course_assignments(course_id: str):
    if not query_one("SELECT CourseID FROM Courses WHERE CourseID = %s", (course_id,)):
        return jsonify({"error": "Course not found"}), 404

    assignments = query_all(
        """SELECT AssignmentID, CourseID, Title, Description,
                  DueDate, MaxGrade, CreatedAt
           FROM Assignments
           WHERE CourseID = %s
           ORDER BY DueDate NULLS LAST, CreatedAt""",
        (course_id,),
    )
    return jsonify(assignments), 200


@assignments_bp.post("/courses/<course_id>/assignments")
@jwt_required()
def create_assignment(course_id: str):
    role = get_jwt().get("role", "")
    if role not in ("Lecturer", "Admin"):
        return jsonify({"error": "Only lecturers and admins can create assignments"}), 403

    if not query_one("SELECT CourseID FROM Courses WHERE CourseID = %s", (course_id,)):
        return jsonify({"error": "Course not found"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    title       = (data.get("title") or "").strip()
    description = data.get("description") or ""
    due_date    = data.get("due_date")
    max_grade   = float(data.get("max_grade", 100))

    if not title:
        return jsonify({"error": "title is required"}), 400
    if max_grade <= 0:
        return jsonify({"error": "max_grade must be greater than 0"}), 400

    assignment = execute_returning(
        """INSERT INTO Assignments (CourseID, Title, Description, DueDate, MaxGrade)
           VALUES (%s, %s, %s, %s, %s)
           RETURNING AssignmentID, CourseID, Title, Description,
                     DueDate, MaxGrade, CreatedAt""",
        (course_id, title, description, due_date, max_grade),
    )
    return jsonify(assignment), 201


# ── Submissions ───────────────────────────────────────────────────────────────


@assignments_bp.post("/assignments/<int:assignment_id>/submit")
@jwt_required()
def submit_assignment(assignment_id: int):
    role = get_jwt().get("role", "")
    if role != "Student":
        return jsonify({"error": "Only students can submit assignments"}), 403

    assignment = query_one(
        "SELECT AssignmentID, DueDate FROM Assignments WHERE AssignmentID = %s",
        (assignment_id,),
    )
    if not assignment:
        return jsonify({"error": "Assignment not found"}), 404

    student_id = get_jwt_identity()

    if query_one(
        "SELECT SubmissionID FROM Submissions WHERE AssignmentID = %s AND StudentID = %s",
        (assignment_id, student_id),
    ):
        return jsonify({"error": "You have already submitted this assignment"}), 409

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    content = (data.get("content") or "").strip()
    if not content:
        return jsonify({"error": "content is required"}), 400

    submission = execute_returning(
        """INSERT INTO Submissions (AssignmentID, StudentID, Content)
           VALUES (%s, %s, %s)
           RETURNING SubmissionID, AssignmentID, StudentID, Content, SubmittedAt""",
        (assignment_id, student_id, content),
    )
    return jsonify(submission), 201


@assignments_bp.get("/assignments/<int:assignment_id>/submissions")
@jwt_required()
def get_submissions(assignment_id: int):
    """
    Lecturers/Admins see all submissions.
    Students see only their own submission.
    """
    role       = get_jwt().get("role", "")
    caller     = get_jwt_identity()

    if not query_one(
        "SELECT AssignmentID FROM Assignments WHERE AssignmentID = %s", (assignment_id,)
    ):
        return jsonify({"error": "Assignment not found"}), 404

    if role in ("Lecturer", "Admin"):
        submissions = query_all(
            """SELECT s.SubmissionID, s.AssignmentID, s.StudentID,
                      u.Name AS StudentName, s.Content, s.SubmittedAt,
                      g.Grade, g.GradedAt
               FROM Submissions s
               LEFT JOIN Users u  ON s.StudentID    = u.UserID
               LEFT JOIN Grades g ON s.SubmissionID = g.SubmissionID
               WHERE s.AssignmentID = %s
               ORDER BY s.SubmittedAt""",
            (assignment_id,),
        )
    else:
        submissions = query_all(
            """SELECT s.SubmissionID, s.AssignmentID, s.StudentID,
                      s.Content, s.SubmittedAt,
                      g.Grade, g.GradedAt
               FROM Submissions s
               LEFT JOIN Grades g ON s.SubmissionID = g.SubmissionID
               WHERE s.AssignmentID = %s AND s.StudentID = %s""",
            (assignment_id, caller),
        )

    return jsonify(submissions), 200


# ── Grading ───────────────────────────────────────────────────────────────────


@assignments_bp.post("/submissions/<int:submission_id>/grade")
@jwt_required()
def grade_submission(submission_id: int):
    role = get_jwt().get("role", "")
    if role not in ("Lecturer", "Admin"):
        return jsonify({"error": "Only lecturers and admins can grade submissions"}), 403

    submission = query_one(
        """SELECT s.SubmissionID, a.MaxGrade
           FROM Submissions s
           JOIN Assignments a ON s.AssignmentID = a.AssignmentID
           WHERE s.SubmissionID = %s""",
        (submission_id,),
    )
    if not submission:
        return jsonify({"error": "Submission not found"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    try:
        grade = float(data.get("grade"))
    except (TypeError, ValueError):
        return jsonify({"error": "grade must be a number"}), 400

    if grade < 0 or grade > float(submission["maxgrade"]):
        return jsonify({
            "error": f"grade must be between 0 and {submission['maxgrade']}"
        }), 400

    graded_by = get_jwt_identity()
    # Upsert: update grade if already graded
    result = execute_returning(
        """INSERT INTO Grades (SubmissionID, Grade, GradedBy)
           VALUES (%s, %s, %s)
           ON CONFLICT (SubmissionID) DO UPDATE
               SET Grade    = EXCLUDED.Grade,
                   GradedBy = EXCLUDED.GradedBy,
                   GradedAt = NOW()
           RETURNING GradeID, SubmissionID, Grade, GradedBy, GradedAt""",
        (submission_id, grade, graded_by),
    )
    return jsonify(result), 200


# ── Student average ───────────────────────────────────────────────────────────


@assignments_bp.get("/students/<student_id>/average")
@jwt_required()
def get_student_average(student_id: str):
    """Return the overall grade average (as a percentage) for a student."""
    row = query_one(
        """SELECT ROUND(
                AVG((g.Grade / NULLIF(a.MaxGrade, 0)) * 100)::NUMERIC,
                2
           ) AS average
           FROM Submissions s
           JOIN Grades      g ON s.SubmissionID = g.SubmissionID
           JOIN Assignments a ON s.AssignmentID = a.AssignmentID
           WHERE s.StudentID = %s""",
        (student_id,),
    )
    average = float(row["average"]) if row and row["average"] is not None else None
    return jsonify({"student_id": student_id, "overall_average": average}), 200
