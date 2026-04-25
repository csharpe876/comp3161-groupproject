"""
Forum, thread, and nested-reply routes.
Replies support arbitrary nesting (Reddit-style) via a self-referential
ParentReplyID column.  Retrieval uses a recursive CTE to fetch the entire
reply tree in one query.
"""
from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from db import execute_returning, query_all, query_one

forums_bp = Blueprint("forums", __name__)


# ── Forums ────────────────────────────────────────────────────────────────────


@forums_bp.get("/courses/<course_id>/forums")
@jwt_required()
def get_course_forums(course_id: str):
    if not query_one("SELECT CourseID FROM Courses WHERE CourseID = %s", (course_id,)):
        return jsonify({"error": "Course not found"}), 404

    forums = query_all(
        """SELECT f.ForumID, f.CourseID, f.Title, f.Description,
                  f.CreatedBy, u.Name AS CreatedByName, f.CreatedAt,
                  COUNT(t.ThreadID) AS ThreadCount
           FROM Forums f
           LEFT JOIN Users u             ON f.CreatedBy = u.UserID
           LEFT JOIN DiscussionThreads t ON f.ForumID   = t.ForumID
           WHERE f.CourseID = %s
           GROUP BY f.ForumID, f.CourseID, f.Title, f.Description,
                    f.CreatedBy, u.Name, f.CreatedAt
           ORDER BY f.CreatedAt DESC""",
        (course_id,),
    )
    return jsonify(forums), 200


@forums_bp.post("/courses/<course_id>/forums")
@jwt_required()
def create_forum(course_id: str):
    role = get_jwt().get("role", "")
    if role not in ("Lecturer", "Admin"):
        return jsonify({"error": "Only lecturers and admins can create forums"}), 403

    if not query_one("SELECT CourseID FROM Courses WHERE CourseID = %s", (course_id,)):
        return jsonify({"error": "Course not found"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    title       = (data.get("title") or "").strip()
    description = data.get("description") or ""

    if not title:
        return jsonify({"error": "title is required"}), 400

    forum = execute_returning(
        """INSERT INTO Forums (CourseID, Title, Description, CreatedBy)
           VALUES (%s, %s, %s, %s)
           RETURNING ForumID, CourseID, Title, Description, CreatedBy, CreatedAt""",
        (course_id, title, description, get_jwt_identity()),
    )
    return jsonify(forum), 201


# ── Threads ───────────────────────────────────────────────────────────────────


@forums_bp.get("/forums/<int:forum_id>/threads")
@jwt_required()
def get_forum_threads(forum_id: int):
    forum = query_one("SELECT ForumID, Title FROM Forums WHERE ForumID = %s", (forum_id,))
    if not forum:
        return jsonify({"error": "Forum not found"}), 404

    threads = query_all(
        """SELECT t.ThreadID, t.ForumID, t.UserID, u.Name AS AuthorName,
                  t.Title, t.Content, t.CreatedAt,
                  COUNT(r.ReplyID) AS ReplyCount
           FROM DiscussionThreads t
           LEFT JOIN Users u        ON t.UserID   = u.UserID
           LEFT JOIN ThreadReplies r ON t.ThreadID = r.ThreadID
           WHERE t.ForumID = %s
           GROUP BY t.ThreadID, t.ForumID, t.UserID, u.Name,
                    t.Title, t.Content, t.CreatedAt
           ORDER BY t.CreatedAt DESC""",
        (forum_id,),
    )
    return jsonify({"forum": forum, "threads": threads}), 200


@forums_bp.post("/forums/<int:forum_id>/threads")
@jwt_required()
def create_thread(forum_id: int):
    if not query_one("SELECT ForumID FROM Forums WHERE ForumID = %s", (forum_id,)):
        return jsonify({"error": "Forum not found"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    title   = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()

    if not title or not content:
        return jsonify({"error": "title and content are required"}), 400

    thread = execute_returning(
        """INSERT INTO DiscussionThreads (ForumID, UserID, Title, Content)
           VALUES (%s, %s, %s, %s)
           RETURNING ThreadID, ForumID, UserID, Title, Content, CreatedAt""",
        (forum_id, get_jwt_identity(), title, content),
    )
    return jsonify(thread), 201


@forums_bp.get("/threads/<int:thread_id>")
@jwt_required()
def get_thread(thread_id: int):
    """Return the thread and its full reply tree (depth-first via CTE)."""
    thread = query_one(
        """SELECT t.ThreadID, t.ForumID, t.UserID, u.Name AS AuthorName,
                  t.Title, t.Content, t.CreatedAt
           FROM DiscussionThreads t
           LEFT JOIN Users u ON t.UserID = u.UserID
           WHERE t.ThreadID = %s""",
        (thread_id,),
    )
    if not thread:
        return jsonify({"error": "Thread not found"}), 404

    # Recursive CTE: fetches the entire reply tree in a single round-trip
    replies = query_all(
        """WITH RECURSIVE reply_tree AS (
               SELECT r.ReplyID, r.ThreadID, r.ParentReplyID, r.UserID,
                      u.Name AS AuthorName, r.Content, r.CreatedAt,
                      0 AS depth
               FROM ThreadReplies r
               LEFT JOIN Users u ON r.UserID = u.UserID
               WHERE r.ThreadID = %s AND r.ParentReplyID IS NULL

               UNION ALL

               SELECT r.ReplyID, r.ThreadID, r.ParentReplyID, r.UserID,
                      u.Name AS AuthorName, r.Content, r.CreatedAt,
                      rt.depth + 1
               FROM ThreadReplies r
               LEFT JOIN Users u   ON r.UserID        = u.UserID
               JOIN reply_tree rt  ON r.ParentReplyID = rt.ReplyID
           )
           SELECT * FROM reply_tree ORDER BY depth, CreatedAt""",
        (thread_id,),
    )
    return jsonify({"thread": thread, "replies": replies}), 200


# ── Replies ───────────────────────────────────────────────────────────────────


@forums_bp.post("/threads/<int:thread_id>/replies")
@jwt_required()
def reply_to_thread(thread_id: int):
    """Direct reply to a thread (ParentReplyID = NULL)."""
    if not query_one(
        "SELECT ThreadID FROM DiscussionThreads WHERE ThreadID = %s", (thread_id,)
    ):
        return jsonify({"error": "Thread not found"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    content = (data.get("content") or "").strip()
    if not content:
        return jsonify({"error": "content is required"}), 400

    reply = execute_returning(
        """INSERT INTO ThreadReplies (ThreadID, ParentReplyID, UserID, Content)
           VALUES (%s, NULL, %s, %s)
           RETURNING ReplyID, ThreadID, ParentReplyID, UserID, Content, CreatedAt""",
        (thread_id, get_jwt_identity(), content),
    )
    return jsonify(reply), 201


@forums_bp.post("/replies/<int:reply_id>/replies")
@jwt_required()
def reply_to_reply(reply_id: int):
    """Nested reply to an existing reply."""
    parent = query_one(
        "SELECT ReplyID, ThreadID FROM ThreadReplies WHERE ReplyID = %s", (reply_id,)
    )
    if not parent:
        return jsonify({"error": "Reply not found"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    content = (data.get("content") or "").strip()
    if not content:
        return jsonify({"error": "content is required"}), 400

    reply = execute_returning(
        """INSERT INTO ThreadReplies (ThreadID, ParentReplyID, UserID, Content)
           VALUES (%s, %s, %s, %s)
           RETURNING ReplyID, ThreadID, ParentReplyID, UserID, Content, CreatedAt""",
        (parent["threadid"], reply_id, get_jwt_identity(), content),
    )
    return jsonify(reply), 201
