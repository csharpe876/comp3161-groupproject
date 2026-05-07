"""
Content model — all database operations for ContentSections and CourseContent.
"""
from __future__ import annotations

from db import execute_returning, query_all, query_one


def get_sections_for_course(course_id: str) -> list[dict]:
    """
    Return all sections for a course, each populated with its content items.
    """
    sections = query_all(
        """SELECT SectionID, SectionName, OrderIndex, CreatedAt
           FROM ContentSections
           WHERE CourseID = %s
           ORDER BY OrderIndex, CreatedAt""",
        (course_id,),
    )
    for sec in sections:
        sec["content"] = query_all(
            """SELECT ContentID, SectionID, Title, ContentType,
                      ContentURL, Description, CreatedAt
               FROM CourseContent
               WHERE SectionID = %s
               ORDER BY CreatedAt""",
            (sec["sectionid"],),
        )
    return sections


def get_section_by_id(section_id: int) -> dict | None:
    """Return a minimal section row, or None if not found."""
    return query_one(
        "SELECT SectionID FROM ContentSections WHERE SectionID = %s",
        (section_id,),
    )


def get_section_with_course(section_id: int) -> dict | None:
    """
    Return the LecID of the course this section belongs to,
    used to authorise lecturer-scoped write operations.
    """
    return query_one(
        """SELECT c.LecID
           FROM ContentSections cs
           JOIN Courses c ON cs.CourseID = c.CourseID
           WHERE cs.SectionID = %s""",
        (section_id,),
    )


def create_section(
    course_id: str,
    section_name: str,
    order_index: int,
) -> dict | None:
    """Insert a new section and return the created row."""
    return execute_returning(
        """INSERT INTO ContentSections (CourseID, SectionName, OrderIndex)
           VALUES (%s, %s, %s)
           RETURNING SectionID, CourseID, SectionName, OrderIndex, CreatedAt""",
        (course_id, section_name, order_index),
    )


def add_item(
    section_id: int,
    title: str,
    content_type: str,
    content_url: str,
    description: str,
) -> dict | None:
    """Insert a content item into a section and return the created row."""
    return execute_returning(
        """INSERT INTO CourseContent
               (SectionID, Title, ContentType, ContentURL, Description)
           VALUES (%s, %s, %s, %s, %s)
           RETURNING ContentID, SectionID, Title, ContentType,
                     ContentURL, Description, CreatedAt""",
        (section_id, title, content_type, content_url, description),
    )
