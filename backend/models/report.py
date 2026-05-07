"""
Report model — queries for the five materialised views used in the Admin panel.
"""
from __future__ import annotations

from db import query_all


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
