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


# ── Constraint checks ─────────────────────────────────────────────────────────

def check_min_students() -> dict:
    """(a) Verify at least 100,000 students exist."""
    row = query_one("SELECT COUNT(*) AS count FROM Users WHERE AccountType = 'Student'")
    count = row["count"]
    return {"constraint": "at_least_100000_students", "count": count, "passes": count >= 100000}


def check_min_courses() -> dict:
    """(b) Verify at least 200 courses exist."""
    row = query_one("SELECT COUNT(*) AS count FROM Courses")
    count = row["count"]
    return {"constraint": "at_least_200_courses", "count": count, "passes": count >= 200}


def check_students_max_6() -> dict:
    """(c) Students enrolled in more than 6 courses — should be empty."""
    violations = query_all(
        """
        SELECT u.UserID AS student_id, u.Name AS name,
               COUNT(e.CourseID) AS enrolled_count
        FROM   Users u
        JOIN   Enrolled e ON u.UserID = e.UserID
        WHERE  u.AccountType = 'Student'
        GROUP BY u.UserID, u.Name
        HAVING COUNT(e.CourseID) > 6
        ORDER BY enrolled_count DESC
        """
    )
    return {"constraint": "no_student_over_6_courses", "violations": violations, "passes": len(violations) == 0}


def check_students_min_3() -> dict:
    """(d) Students enrolled in fewer than 3 courses — should be empty."""
    violations = query_all(
        """
        SELECT u.UserID AS student_id, u.Name AS name,
               COUNT(e.CourseID) AS enrolled_count
        FROM   Users u
        LEFT JOIN Enrolled e ON u.UserID = e.UserID
        WHERE  u.AccountType = 'Student'
        GROUP BY u.UserID, u.Name
        HAVING COUNT(e.CourseID) < 3
        ORDER BY enrolled_count
        """
    )
    return {"constraint": "all_students_min_3_courses", "violations": violations, "passes": len(violations) == 0}


def check_courses_min_10() -> dict:
    """(e) Courses with fewer than 10 enrolled students — should be empty."""
    violations = query_all(
        """
        SELECT c.CourseID AS course_id, c.CourseTitle AS title,
               COUNT(e.UserID) AS enrolled_count
        FROM   Courses c
        LEFT JOIN Enrolled e ON c.CourseID = e.CourseID
        GROUP BY c.CourseID, c.CourseTitle
        HAVING COUNT(e.UserID) < 10
        ORDER BY enrolled_count
        """
    )
    return {"constraint": "all_courses_min_10_members", "violations": violations, "passes": len(violations) == 0}


def check_lecturers_max_5() -> dict:
    """(f) Lecturers teaching more than 5 courses — should be empty."""
    violations = query_all(
        """
        SELECT u.UserID AS lec_id, u.Name AS name,
               COUNT(c.CourseID) AS course_count
        FROM   Users u
        JOIN   Courses c ON u.UserID = c.LecID
        WHERE  u.AccountType = 'Lecturer'
        GROUP BY u.UserID, u.Name
        HAVING COUNT(c.CourseID) > 5
        ORDER BY course_count DESC
        """
    )
    return {"constraint": "no_lecturer_over_5_courses", "violations": violations, "passes": len(violations) == 0}


def check_lecturers_min_1() -> dict:
    """(g) Lecturers teaching zero courses — should be empty."""
    violations = query_all(
        """
        SELECT u.UserID AS lec_id, u.Name AS name
        FROM   Users u
        LEFT JOIN Courses c ON u.UserID = c.LecID
        WHERE  u.AccountType = 'Lecturer'
        GROUP BY u.UserID, u.Name
        HAVING COUNT(c.CourseID) < 1
        """
    )
    return {"constraint": "all_lecturers_min_1_course", "violations": violations, "passes": len(violations) == 0}
