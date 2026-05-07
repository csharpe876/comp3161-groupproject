"""
Course model — all database operations for Courses and Enrollment.
"""
from __future__ import annotations

from db import execute, execute_returning, query_all, query_one


# ── Courses ───────────────────────────────────────────────────────────────────

def get_all() -> list[dict]:
    """Return every course with lecturer name and enrolled-student count."""
    return query_all(
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


def get_by_id(course_id: str) -> dict | None:
    """Return a single course with lecturer name, or None."""
    return query_one(
        """SELECT c.CourseID, c.CourseTitle, c.CourseCode, c.Description,
                  c.LecID, u.Name AS LecturerName, c.CreatedAt
           FROM Courses c
           LEFT JOIN Users u ON c.LecID = u.UserID
           WHERE c.CourseID = %s""",
        (course_id,),
    )


def id_or_code_taken(course_id: str, code: str) -> bool:
    """Return True if either the CourseID or CourseCode is already in use."""
    return bool(
        query_one(
            "SELECT CourseID FROM Courses WHERE CourseID = %s OR CourseCode = %s",
            (course_id, code),
        )
    )


def create(
    course_id: str,
    title: str,
    code: str,
    description: str,
    lec_id: str | None,
) -> dict | None:
    """Insert a new course and return the created row."""
    return execute_returning(
        """INSERT INTO Courses (CourseID, CourseTitle, CourseCode, Description, LecID)
           VALUES (%s, %s, %s, %s, %s)
           RETURNING CourseID, CourseTitle, CourseCode, Description, LecID, CreatedAt""",
        (course_id, title, code, description, lec_id),
    )


def assign_lecturer(course_id: str, lec_id: str) -> int:
    """Update the LecID for a course and return the number of affected rows."""
    return execute(
        "UPDATE Courses SET LecID = %s WHERE CourseID = %s",
        (lec_id, course_id),
    )


def lecturer_course_count(lec_id: str) -> int:
    """Return how many courses the given lecturer currently teaches."""
    row = query_one(
        "SELECT COUNT(*) AS cnt FROM Courses WHERE LecID = %s", (lec_id,)
    )
    return int(row["cnt"]) if row else 0


def get_for_student(student_id: str) -> list[dict]:
    """Return all courses a student is enrolled in."""
    return query_all(
        """SELECT c.CourseID, c.CourseTitle, c.CourseCode, c.Description,
                  c.LecID, u.Name AS LecturerName, e.EnrolledAt
           FROM Courses c
           JOIN Enrolled e ON c.CourseID = e.CourseID
           LEFT JOIN Users u ON c.LecID = u.UserID
           WHERE e.UserID = %s
           ORDER BY c.CourseID""",
        (student_id,),
    )


def get_for_lecturer(lecturer_id: str) -> list[dict]:
    """Return all courses taught by a lecturer, with enrolled-student count."""
    return query_all(
        """SELECT c.CourseID, c.CourseTitle, c.CourseCode, c.Description,
                  c.CreatedAt, COUNT(e.UserID) AS EnrolledCount
           FROM Courses c
           LEFT JOIN Enrolled e ON c.CourseID = e.CourseID
           WHERE c.LecID = %s
           GROUP BY c.CourseID, c.CourseTitle, c.CourseCode, c.Description, c.CreatedAt
           ORDER BY c.CourseID""",
        (lecturer_id,),
    )


# ── Enrollment ────────────────────────────────────────────────────────────────

def is_enrolled(student_id: str, course_id: str) -> bool:
    """Return True if the student is already enrolled in the course."""
    return bool(
        query_one(
            "SELECT 1 FROM Enrolled WHERE UserID = %s AND CourseID = %s",
            (student_id, course_id),
        )
    )


def enrollment_count(student_id: str) -> int:
    """Return the number of courses a student is currently enrolled in."""
    row = query_one(
        "SELECT COUNT(*) AS cnt FROM Enrolled WHERE UserID = %s", (student_id,)
    )
    return int(row["cnt"]) if row else 0


def enroll(student_id: str, course_id: str) -> int:
    """Insert an enrollment record and return the affected row count."""
    return execute(
        "INSERT INTO Enrolled (UserID, CourseID) VALUES (%s, %s)",
        (student_id, course_id),
    )


def get_members(course_id: str) -> dict | None:
    """
    Return the full member structure for a course, or None if not found.

    Structure: {course_id, course_title, lecturer (or None), students, total_members}
    """
    course = query_one(
        """SELECT c.CourseID, c.CourseTitle, c.LecID,
                  u.Name AS LecturerName, u.Email AS LecturerEmail
           FROM Courses c
           LEFT JOIN Users u ON c.LecID = u.UserID
           WHERE c.CourseID = %s""",
        (course_id,),
    )
    if not course:
        return None

    students = query_all(
        """SELECT u.UserID, u.Name, u.Email, e.EnrolledAt
           FROM Users u
           JOIN Enrolled e ON u.UserID = e.UserID
           WHERE e.CourseID = %s
           ORDER BY u.Name""",
        (course_id,),
    )

    return {
        "course_id":    course["courseid"],
        "course_title": course["coursetitle"],
        "lecturer": {
            "userid": course["lecid"],
            "name":   course["lecturername"],
            "email":  course["lectureremail"],
        } if course["lecid"] else None,
        "students":      students,
        "total_members": len(students) + (1 if course["lecid"] else 0),
    }
