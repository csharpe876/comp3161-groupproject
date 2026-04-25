"""
Calendar event routes.
"""
from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from db import execute_returning, query_all, query_one

calendar_bp = Blueprint("calendar", __name__)


@calendar_bp.get("/courses/<course_id>/events")
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


@calendar_bp.post("/courses/<course_id>/events")
@jwt_required()
def create_course_event(course_id: str):
    """Lecturer or Admin: create a calendar event for a course."""
    role = get_jwt().get("role", "")
    if role not in ("Lecturer", "Admin"):
        return jsonify({"error": "Only lecturers and admins can create events"}), 403

    if not query_one("SELECT CourseID FROM Courses WHERE CourseID = %s", (course_id,)):
        return jsonify({"error": "Course not found"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    title      = (data.get("title") or "").strip()
    description = data.get("description") or ""
    event_date = data.get("event_date")
    event_time = data.get("event_time")

    if not title or not event_date:
        return jsonify({"error": "title and event_date are required"}), 400

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


@calendar_bp.get("/students/<student_id>/events")
@jwt_required()
def get_student_events_by_date(student_id: str):
    """Return all events for a specific date across a student's enrolled courses.

    Query parameter: ?date=YYYY-MM-DD  (required)
    """
    event_date = request.args.get("date")
    if not event_date:
        return jsonify({"error": "Query parameter ?date=YYYY-MM-DD is required"}), 400

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
