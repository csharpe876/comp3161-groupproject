"""
Assignment, Submission, and Grade models.
"""
from __future__ import annotations

from db import execute_returning, query_all, query_one


# ── Assignments ───────────────────────────────────────────────────────────────

def get_all_for_course(course_id: str) -> list[dict]:
    """Return all assignments for a course, ordered by due date."""
    return query_all(
        """SELECT AssignmentID, CourseID, Title, Description,
                  DueDate, MaxGrade, CreatedAt
           FROM Assignments
           WHERE CourseID = %s
           ORDER BY DueDate NULLS LAST, CreatedAt""",
        (course_id,),
    )


def get_by_id(assignment_id: int) -> dict | None:
    """Return a lightweight assignment row (id, course, due date)."""
    return query_one(
        "SELECT AssignmentID, CourseID, DueDate FROM Assignments WHERE AssignmentID = %s",
        (assignment_id,),
    )


def get_with_course(assignment_id: int) -> dict | None:
    """Return an assignment joined with its course's LecID and MaxGrade."""
    return query_one(
        """SELECT s.SubmissionID, a.MaxGrade, c.LecID
           FROM Submissions s
           JOIN Assignments a ON s.AssignmentID = a.AssignmentID
           JOIN Courses c     ON a.CourseID      = c.CourseID
           WHERE s.SubmissionID = %s""",
        (assignment_id,),
    )


def create(
    course_id: str,
    title: str,
    description: str,
    due_date,
    max_grade: float,
) -> dict | None:
    """Insert a new assignment and return the created row."""
    return execute_returning(
        """INSERT INTO Assignments (CourseID, Title, Description, DueDate, MaxGrade)
           VALUES (%s, %s, %s, %s, %s)
           RETURNING AssignmentID, CourseID, Title, Description,
                     DueDate, MaxGrade, CreatedAt""",
        (course_id, title, description, due_date, max_grade),
    )


# ── Submissions ───────────────────────────────────────────────────────────────

def submission_exists(assignment_id: int, student_id: str) -> bool:
    """Return True if the student has already submitted this assignment."""
    return bool(
        query_one(
            "SELECT SubmissionID FROM Submissions "
            "WHERE AssignmentID = %s AND StudentID = %s",
            (assignment_id, student_id),
        )
    )


def create_submission(
    assignment_id: int,
    student_id: str,
    content: str,
) -> dict | None:
    """Insert a submission and return the created row."""
    return execute_returning(
        """INSERT INTO Submissions (AssignmentID, StudentID, Content)
           VALUES (%s, %s, %s)
           RETURNING SubmissionID, AssignmentID, StudentID, Content, SubmittedAt""",
        (assignment_id, student_id, content),
    )


def get_submission_for_grading(submission_id: int) -> dict | None:
    """
    Return submission info needed to authorise grading:
    MaxGrade and the LecID of the course this assignment belongs to.
    """
    return query_one(
        """SELECT s.SubmissionID, a.MaxGrade, c.LecID
           FROM Submissions s
           JOIN Assignments a ON s.AssignmentID = a.AssignmentID
           JOIN Courses c     ON a.CourseID      = c.CourseID
           WHERE s.SubmissionID = %s""",
        (submission_id,),
    )


def get_all_submissions(assignment_id: int) -> list[dict]:
    """Return all submissions for an assignment (staff view, includes grades)."""
    return query_all(
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


def get_student_submissions(assignment_id: int, student_id: str) -> list[dict]:
    """Return a single student's submission for an assignment."""
    return query_all(
        """SELECT s.SubmissionID, s.AssignmentID, s.StudentID,
                  s.Content, s.SubmittedAt,
                  g.Grade, g.GradedAt
           FROM Submissions s
           LEFT JOIN Grades g ON s.SubmissionID = g.SubmissionID
           WHERE s.AssignmentID = %s AND s.StudentID = %s""",
        (assignment_id, student_id),
    )


# ── Grades ────────────────────────────────────────────────────────────────────

def upsert_grade(
    submission_id: int,
    grade: float,
    graded_by: str,
) -> dict | None:
    """
    Insert or update a grade for a submission (upsert on SubmissionID).
    Returns the resulting grade row.
    """
    return execute_returning(
        """INSERT INTO Grades (SubmissionID, Grade, GradedBy)
           VALUES (%s, %s, %s)
           ON CONFLICT (SubmissionID) DO UPDATE
               SET Grade    = EXCLUDED.Grade,
                   GradedBy = EXCLUDED.GradedBy,
                   GradedAt = NOW()
           RETURNING GradeID, SubmissionID, Grade, GradedBy, GradedAt""",
        (submission_id, grade, graded_by),
    )


def get_student_average(student_id: str) -> float | None:
    """
    Return the overall grade average as a percentage for a student,
    or None if the student has no graded submissions.
    """
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
    return float(row["average"]) if row and row["average"] is not None else None
