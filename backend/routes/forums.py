"""
Forums controller — HTTP handlers for forums, threads, and nested replies.
All data-access logic lives in models.forum and models.course.
"""
from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from models import forum as forum_model
from models import course as course_model

forums_bp = Blueprint("forums", __name__)


# ── Forums ────────────────────────────────────────────────────────────────────


@forums_bp.route("/courses/<course_id>/forums", methods=["GET"])
@jwt_required()
def get_course_forums(course_id: str):
    if not course_model.get_by_id(course_id):
        return jsonify({"error": "Course not found"}), 404
    return jsonify(forum_model.get_all_for_course(course_id)), 200


@forums_bp.route("/courses/<course_id>/forums", methods=["POST"])
@jwt_required()
def create_forum(course_id: str):
    role = get_jwt().get("role", "")
    if role not in ("Lecturer", "Admin"):
        return jsonify({"error": "Only lecturers and admins can create forums"}), 403

    if not course_model.get_by_id(course_id):
        return jsonify({"error": "Course not found"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    title       = (data.get("title") or "").strip()
    description = data.get("description") or ""

    if not title:
        return jsonify({"error": "title is required"}), 400

    forum = forum_model.create(course_id, title, description, get_jwt_identity())
    return jsonify(forum), 201


# ── Threads ───────────────────────────────────────────────────────────────────


@forums_bp.route("/forums/<int:forum_id>/threads", methods=["GET"])
@jwt_required()
def get_forum_threads(forum_id: int):
    forum = forum_model.get_by_id(forum_id)
    if not forum:
        return jsonify({"error": "Forum not found"}), 404
    threads = forum_model.get_threads_for_forum(forum_id)
    return jsonify({"forum": forum, "threads": threads}), 200


@forums_bp.route("/forums/<int:forum_id>/threads", methods=["POST"])
@jwt_required()
def create_thread(forum_id: int):
    if not forum_model.get_by_id(forum_id):
        return jsonify({"error": "Forum not found"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    title   = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()

    if not title or not content:
        return jsonify({"error": "title and content are required"}), 400

    thread = forum_model.create_thread(forum_id, get_jwt_identity(), title, content)
    return jsonify(thread), 201


@forums_bp.route("/threads/<int:thread_id>", methods=["GET"])
@jwt_required()
def get_thread(thread_id: int):
    """Return the thread and its full reply tree (depth-first via CTE)."""
    thread = forum_model.get_thread_by_id(thread_id)
    if not thread:
        return jsonify({"error": "Thread not found"}), 404
    replies = forum_model.get_reply_tree(thread_id)
    return jsonify({"thread": thread, "replies": replies}), 200


# ── Replies ───────────────────────────────────────────────────────────────────


@forums_bp.route("/threads/<int:thread_id>/replies", methods=["POST"])
@jwt_required()
def reply_to_thread(thread_id: int):
    """Direct reply to a thread (ParentReplyID = NULL)."""
    if not forum_model.get_thread_by_id(thread_id):
        return jsonify({"error": "Thread not found"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    content = (data.get("content") or "").strip()
    if not content:
        return jsonify({"error": "content is required"}), 400

    reply = forum_model.create_reply(thread_id, None, get_jwt_identity(), content)
    return jsonify(reply), 201


@forums_bp.route("/replies/<int:reply_id>/replies", methods=["POST"])
@jwt_required()
def reply_to_reply(reply_id: int):
    """Nested reply to an existing reply."""
    parent = forum_model.get_reply_by_id(reply_id)
    if not parent:
        return jsonify({"error": "Reply not found"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    content = (data.get("content") or "").strip()
    if not content:
        return jsonify({"error": "content is required"}), 400

    reply = forum_model.create_reply(parent["threadid"], reply_id, get_jwt_identity(), content)
    return jsonify(reply), 201


