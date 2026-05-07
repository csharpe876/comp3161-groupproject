"""
Calendar model — all database operations for CalendarEvents.
"""
from __future__ import annotations

from db import execute_returning, query_all


def get_events_for_course(course_id: str) -> list[dict]:
    """Return all calendar events for a course, ordered chronologically."""
    return query_all(
        """SELECT e.EventID, e.CourseID, e.Title, e.Description,
                  e.EventDate, e.EventTime, e.CreatedBy,
                  u.Name AS CreatedByName, e.CreatedAt
           FROM CalendarEvents e
           LEFT JOIN Users u ON e.CreatedBy = u.UserID
           WHERE e.CourseID = %s
           ORDER BY e.EventDate, e.EventTime NULLS LAST""",
        (course_id,),
    )


def create_event(
    course_id: str,
    title: str,
    description: str,
    event_date: str,
    event_time,
    created_by: str,
) -> dict | None:
    """Insert a new calendar event and return the created row."""
    return execute_returning(
        """INSERT INTO CalendarEvents
               (CourseID, Title, Description, EventDate, EventTime, CreatedBy)
           VALUES (%s, %s, %s, %s, %s, %s)
           RETURNING EventID, CourseID, Title, Description,
                     EventDate, EventTime, CreatedBy, CreatedAt""",
        (course_id, title, description, event_date, event_time, created_by),
    )


def get_student_events_for_date(student_id: str, event_date: str) -> list[dict]:
    """
    Return all events on a given date across all courses a student is enrolled in.
    """
    return query_all(
        """SELECT e.EventID, c.CourseID, c.CourseTitle, c.CourseCode,
                  e.Title, e.Description, e.EventDate, e.EventTime, e.CreatedAt
           FROM CalendarEvents e
           JOIN Courses  c  ON e.CourseID  = c.CourseID
           JOIN Enrolled en ON c.CourseID  = en.CourseID AND en.UserID = %s
           WHERE e.EventDate = %s
           ORDER BY e.EventTime NULLS LAST""",
        (student_id, event_date),
    )
