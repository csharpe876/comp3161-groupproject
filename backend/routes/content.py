"""
Content controller — HTTP handlers for course sections and content items.
All data-access logic lives in models.content.
"""
from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from models import content as content_model
from models import course as course_model

api = Blueprint("content", __name__)


@api.route("/courses/<course_id>/content", methods=["GET"])
@jwt_required()
def get_course_content(course_id: str):
    """Return all sections for a course, each with their content items."""
    course = course_model.get_by_id(course_id)
    if not course:
        return jsonify({"error": "Course not found"}), 404
    sections = content_model.get_sections_for_course(course_id)
    return jsonify({"course": course, "sections": sections}), 200


@api.route("/courses/<course_id>/sections", methods=["POST"])
@jwt_required()
def create_section(course_id: str):
    """Lecturer or Admin: add a new section to a course."""
    role = get_jwt().get("role", "")
    if role not in ("Lecturer", "Admin"):
        return jsonify({"error": "Only lecturers and admins can add sections"}), 403

    course = course_model.get_by_id(course_id)
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

    section = content_model.create_section(course_id, section_name, order_index)
    return jsonify(section), 201


@api.route("/sections/<int:section_id>/content", methods=["POST"])
@jwt_required()
def add_content_item(section_id: int):
    """Lecturer or Admin: add a content item to a section."""
    role = get_jwt().get("role", "")
    if role not in ("Lecturer", "Admin"):
        return jsonify({"error": "Only lecturers and admins can add content"}), 403

    if not content_model.get_section_by_id(section_id):
        return jsonify({"error": "Section not found"}), 404

    # Lecturers may only add content to sections in courses they teach.
    if role == "Lecturer":
        course_row = content_model.get_section_with_course(section_id)
        if not course_row or course_row["lecid"] != get_jwt_identity():
            return jsonify({"error": "You do not teach the course this section belongs to"}), 403

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    title = (data.get("title") or "").strip()
    content_type = (data.get("content_type") or "").strip().lower()
    content_url = (data.get("content_url") or "").strip()
    description = data.get("description") or ""

    if not all([title, content_type, content_url]):
        return jsonify({"error": "title, content_type, and content_url are required"}), 400

    if content_type not in ("link", "file", "slide"):
        return jsonify({"error": "content_type must be link, file, or slide"}), 400

    # Block javascript:, data:, and other non-HTTP(S) schemes.
    if not content_url.lower().startswith(("https://", "http://")):
        return jsonify({"error": "content_url must begin with https:// or http://"}), 400

    item = content_model.add_item(section_id, title, content_type, content_url, description)
    return jsonify(item), 201
