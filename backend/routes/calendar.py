"""
Calendar event routes.
"""
from __future__ import annotations

from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from db import execute_returning, query_all, query_one

calendar_bp = Blueprint("calendar", __name__)


@calendar_bp.route("/courses/<course_id>/events", methods=["GET"])
@jwt_required()
def get_course_events(course_id: str):
    """Return all calendar events for a course, ordered chronologically."""
    if not query_one("SELECT CourseID FROM Courses WHERE CourseID = %s", (course_id,)):
        return jsonify({"error": "Course not found"}), 404

    events = query_all(
        """SELECT e.EventID, e.CourseID, e.Title, e.Description,
                  e.EventDate, e.EventTime, e.CreatedBy,
                  u.Name AS CreatedByName, e.CreatedAt
           FROM CalendarEvents e
           LEFT JOIN Users u ON e.CreatedBy = u.UserID
           WHERE e.CourseID = %s
           ORDER BY e.EventDate, e.EventTime NULLS LAST""",
        (course_id,),
    )
    return jsonify(events), 200


@calendar_bp.route("/courses/<course_id>/events", methods=["POST"])
@jwt_required()
def create_course_event(course_id: str):
    """Lecturer or Admin: create a calendar event for a course."""
    role = get_jwt().get("role", "")
    if role not in ("Lecturer", "Admin"):
        return jsonify({"error": "Only lecturers and admins can create events"}), 403

    course = query_one("SELECT CourseID, LecID FROM Courses WHERE CourseID = %s", (course_id,))
    if not course:
        return jsonify({"error": "Course not found"}), 404

    # Lecturers may only create events for courses they actually teach.
    if role == "Lecturer" and course["lecid"] != get_jwt_identity():
        return jsonify({"error": "You do not teach this course"}), 403

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    title       = (data.get("title") or "").strip()
    description = data.get("description") or ""
    event_date  = data.get("event_date")
    event_time  = data.get("event_time")

    if not title or not event_date:
        return jsonify({"error": "title and event_date are required"}), 400

    # Validate date format.
    try:
        datetime.strptime(event_date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "event_date must be in YYYY-MM-DD format"}), 400

    # Validate optional time format.
    if event_time:
        valid_time = False
        for fmt in ("%H:%M", "%H:%M:%S"):
            try:
                datetime.strptime(event_time, fmt)
                valid_time = True
                break
            except ValueError:
                pass
        if not valid_time:
            return jsonify({"error": "event_time must be in HH:MM or HH:MM:SS format"}), 400

    created_by = get_jwt_identity()
    event = execute_returning(
        """INSERT INTO CalendarEvents
               (CourseID, Title, Description, EventDate, EventTime, CreatedBy)
           VALUES (%s, %s, %s, %s, %s, %s)
           RETURNING EventID, CourseID, Title, Description,
                     EventDate, EventTime, CreatedBy, CreatedAt""",
        (course_id, title, description, event_date, event_time, created_by),
    )
    return jsonify(event), 201


@calendar_bp.route("/students/<student_id>/events", methods=["GET"])
@jwt_required()
def get_student_events_by_date(student_id: str):
    """Return all events for a specific date across a student's enrolled courses.

    Query parameter: ?date=YYYY-MM-DD  (required)
    """
    # Students may only view their own calendar; Lecturers and Admins may view any.
    caller = get_jwt_identity()
    role   = get_jwt().get("role", "")
    if role not in ("Admin", "Lecturer") and caller != student_id:
        return jsonify({"error": "You may only view your own calendar"}), 403

    event_date = request.args.get("date")
    if not event_date:
        return jsonify({"error": "Query parameter ?date=YYYY-MM-DD is required"}), 400

    # Validate date format before passing to the database.
    try:
        datetime.strptime(event_date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "date must be in YYYY-MM-DD format"}), 400

    events = query_all(
        """SELECT e.EventID, e.CourseID, c.CourseTitle, c.CourseCode,
                  e.Title, e.Description, e.EventDate, e.EventTime, e.CreatedAt
           FROM CalendarEvents e
           JOIN Courses c  ON e.CourseID  = c.CourseID
           JOIN Enrolled en ON c.CourseID = en.CourseID AND en.UserID = %s
           WHERE e.EventDate = %s
           ORDER BY e.EventTime NULLS LAST""",
        (student_id, event_date),
    )
    return jsonify(events), 200
