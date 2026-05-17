"""
Report model — queries for the five materialised views used in the Admin panel,
plus ad-hoc stat queries.
"""
from __future__ import annotations

from db import query_all, query_one


def courses_50plus() -> list[dict]:
    """All courses with 50 or more enrolled students."""
    return query_all("SELECT * FROM v_courses_50plus_students")


def students_5plus() -> list[dict]:
    """All students enrolled in 5 or more courses."""
    return query_all("SELECT * FROM v_students_5plus_courses")


def lecturers_3plus() -> list[dict]:
    """All lecturers who teach 3 or more courses."""
    return query_all("SELECT * FROM v_lecturers_3plus_courses")


def top10_enrolled() -> list[dict]:
    """The 10 most enrolled courses."""
    return query_all("SELECT * FROM v_top10_most_enrolled")


def top10_averages() -> list[dict]:
    """Top 10 students by overall grade average."""
    return query_all("SELECT * FROM v_top10_student_averages")


# ── Ad-hoc stats ─────────────────────────────────────────────────────────────

def total_students() -> dict:
    return query_one(
        "SELECT COUNT(*) AS total_students FROM Users WHERE AccountType = 'Student'"
    )


def total_lecturers() -> dict:
    return query_one(
        "SELECT COUNT(*) AS total_lecturers FROM Users WHERE AccountType = 'Lecturer'"
    )


def total_courses() -> dict:
    return query_one("SELECT COUNT(*) AS total_courses FROM Courses")


def enrollment_per_course() -> list[dict]:
    """Number of enrolled students per course, descending."""
    return query_all(
        """
        SELECT c.CourseID  AS course_id,
               c.CourseTitle AS title,
               COUNT(e.UserID) AS enrolled_count
        FROM   Courses c
        LEFT JOIN Enrolled e ON c.CourseID = e.CourseID
        GROUP BY c.CourseID, c.CourseTitle
        ORDER BY enrolled_count DESC
        """
    )


def courses_per_lecturer() -> list[dict]:
    """Number of courses taught by each lecturer, descending."""
    return query_all(
        """
        SELECT u.UserID AS lec_id,
               u.Name   AS name,
               COUNT(c.CourseID) AS course_count
        FROM   Users u
        LEFT JOIN Courses c ON u.UserID = c.LecID
        WHERE  u.AccountType = 'Lecturer'
        GROUP BY u.UserID, u.Name
        ORDER BY course_count DESC
        """
    )


def students_lt3_courses() -> list[dict]:
    """Students enrolled in fewer than 3 courses."""
    return query_all(
        """
        SELECT u.UserID AS student_id,
               u.Name   AS name,
               COUNT(e.CourseID) AS enrolled_count
        FROM   Users u
        LEFT JOIN Enrolled e ON u.UserID = e.UserID
        WHERE  u.AccountType = 'Student'
        GROUP BY u.UserID, u.Name
        HAVING COUNT(e.CourseID) < 3
        ORDER BY enrolled_count
        """
    )


def lecturers_no_courses() -> list[dict]:
    """Lecturers who are not currently assigned to any course."""
    return query_all(
        """
        SELECT u.UserID AS lec_id,
               u.Name   AS name
        FROM   Users u
        LEFT JOIN Courses c ON u.UserID = c.LecID
        WHERE  u.AccountType = 'Lecturer'
        GROUP BY u.UserID, u.Name
        HAVING COUNT(c.CourseID) < 1
        """
    )
