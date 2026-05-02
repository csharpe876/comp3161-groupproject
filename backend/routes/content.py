"""
Course content routes: sections and content items (links, files, slides).
"""
from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from db import execute_returning, query_all, query_one

content_bp = Blueprint("content", __name__)


@content_bp.route("/courses/<course_id>/content", methods=["GET"])
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


@content_bp.route("/courses/<course_id>/sections", methods=["POST"])
@jwt_required()
def create_section(course_id: str):
    """Lecturer or Admin: add a new section to a course."""
    role = get_jwt().get("role", "")
    if role not in ("Lecturer", "Admin"):
        return jsonify({"error": "Only lecturers and admins can add sections"}), 403

    course = query_one("SELECT CourseID, LecID FROM Courses WHERE CourseID = %s", (course_id,))
    if not course:
        return jsonify({"error": "Course not found"}), 404

    # Lecturers may only add sections to courses they teach.
    if role == "Lecturer" and course["lecid"] != get_jwt_identity():
        return jsonify({"error": "You do not teach this course and cannot add sections to it"}), 403

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    section_name = (data.get("section_name") or "").strip()
    try:
        order_index = int(data.get("order_index", 0))
        if order_index < 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "order_index must be a non-negative integer"}), 400

    if not section_name:
        return jsonify({"error": "section_name is required"}), 400

    section = execute_returning(
        """INSERT INTO ContentSections (CourseID, SectionName, OrderIndex)
           VALUES (%s, %s, %s)
           RETURNING SectionID, CourseID, SectionName, OrderIndex, CreatedAt""",
        (course_id, section_name, order_index),
    )
    return jsonify(section), 201


@content_bp.route("/sections/<int:section_id>/content", methods=["POST"])
@jwt_required()
def add_content_item(section_id: int):
    """Lecturer or Admin: add a content item to a section."""
    role = get_jwt().get("role", "")
    if role not in ("Lecturer", "Admin"):
        return jsonify({"error": "Only lecturers and admins can add content"}), 403

    section = query_one(
        "SELECT SectionID FROM ContentSections WHERE SectionID = %s", (section_id,)
    )
    if not section:
        return jsonify({"error": "Section not found"}), 404

    # Lecturers may only add content to sections in courses they teach.
    if role == "Lecturer":
        course_row = query_one(
            """SELECT c.LecID
               FROM ContentSections cs
               JOIN Courses c ON cs.CourseID = c.CourseID
               WHERE cs.SectionID = %s""",
            (section_id,),
        )
        if not course_row or course_row["lecid"] != get_jwt_identity():
            return jsonify({"error": "You do not teach the course this section belongs to"}), 403

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

    # Block javascript:, data:, and other non-HTTP(S) schemes.
    if not content_url.lower().startswith(("https://", "http://")):
        return jsonify({"error": "content_url must begin with https:// or http://"}), 400

    item = execute_returning(
        """INSERT INTO CourseContent
               (SectionID, Title, ContentType, ContentURL, Description)
           VALUES (%s, %s, %s, %s, %s)
           RETURNING ContentID, SectionID, Title, ContentType,
                     ContentURL, Description, CreatedAt""",
        (section_id, title, content_type, content_url, description),
    )
    return jsonify(item), 201
