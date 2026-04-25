"""
Course content routes: sections and content items (links, files, slides).
"""
from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required

from db import execute_returning, query_all, query_one

content_bp = Blueprint("content", __name__)


@content_bp.get("/courses/<course_id>/content")
@jwt_required()
def get_course_content(course_id: str):
    """Return all sections for a course, each with their content items."""
    course = query_one(
        "SELECT CourseID, CourseTitle FROM Courses WHERE CourseID = %s", (course_id,)
    )
    if not course:
        return jsonify({"error": "Course not found"}), 404

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

    return jsonify({"course": course, "sections": sections}), 200


@content_bp.post("/courses/<course_id>/sections")
@jwt_required()
def create_section(course_id: str):
    """Lecturer or Admin: add a new section to a course."""
    role = get_jwt().get("role", "")
    if role not in ("Lecturer", "Admin"):
        return jsonify({"error": "Only lecturers and admins can add sections"}), 403

    if not query_one("SELECT CourseID FROM Courses WHERE CourseID = %s", (course_id,)):
        return jsonify({"error": "Course not found"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    section_name = (data.get("section_name") or "").strip()
    order_index  = int(data.get("order_index", 0))

    if not section_name:
        return jsonify({"error": "section_name is required"}), 400

    section = execute_returning(
        """INSERT INTO ContentSections (CourseID, SectionName, OrderIndex)
           VALUES (%s, %s, %s)
           RETURNING SectionID, CourseID, SectionName, OrderIndex, CreatedAt""",
        (course_id, section_name, order_index),
    )
    return jsonify(section), 201


@content_bp.post("/sections/<int:section_id>/content")
@jwt_required()
def add_content_item(section_id: int):
    """Lecturer or Admin: add a content item to a section."""
    role = get_jwt().get("role", "")
    if role not in ("Lecturer", "Admin"):
        return jsonify({"error": "Only lecturers and admins can add content"}), 403

    if not query_one(
        "SELECT SectionID FROM ContentSections WHERE SectionID = %s", (section_id,)
    ):
        return jsonify({"error": "Section not found"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    title        = (data.get("title") or "").strip()
    content_type = (data.get("content_type") or "").strip().lower()
    content_url  = (data.get("content_url") or "").strip()
    description  = data.get("description") or ""

    if not all([title, content_type, content_url]):
        return jsonify({"error": "title, content_type, and content_url are required"}), 400

    if content_type not in ("link", "file", "slide"):
        return jsonify({"error": "content_type must be link, file, or slide"}), 400

    item = execute_returning(
        """INSERT INTO CourseContent
               (SectionID, Title, ContentType, ContentURL, Description)
           VALUES (%s, %s, %s, %s, %s)
           RETURNING ContentID, SectionID, Title, ContentType,
                     ContentURL, Description, CreatedAt""",
        (section_id, title, content_type, content_url, description),
    )
    return jsonify(item), 201
