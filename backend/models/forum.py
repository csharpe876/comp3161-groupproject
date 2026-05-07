"""
Forum, Thread, and Reply models.
Replies support arbitrary nesting via a recursive CTE.
"""
from __future__ import annotations

from db import execute_returning, query_all, query_one


# ── Forums ────────────────────────────────────────────────────────────────────

def get_all_for_course(course_id: str) -> list[dict]:
    """Return all forums for a course with thread counts."""
    return query_all(
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


def get_by_id(forum_id: int) -> dict | None:
    """Return a forum row, or None if not found."""
    return query_one(
        "SELECT ForumID, Title FROM Forums WHERE ForumID = %s", (forum_id,)
    )


def create(
    course_id: str,
    title: str,
    description: str,
    created_by: str,
) -> dict | None:
    """Insert a new forum and return the created row."""
    return execute_returning(
        """INSERT INTO Forums (CourseID, Title, Description, CreatedBy)
           VALUES (%s, %s, %s, %s)
           RETURNING ForumID, CourseID, Title, Description, CreatedBy, CreatedAt""",
        (course_id, title, description, created_by),
    )


# ── Threads ───────────────────────────────────────────────────────────────────

def get_threads_for_forum(forum_id: int) -> list[dict]:
    """Return all threads in a forum with author names and reply counts."""
    return query_all(
        """SELECT t.ThreadID, t.ForumID, t.UserID, u.Name AS AuthorName,
                  t.Title, t.Content, t.CreatedAt,
                  COUNT(r.ReplyID) AS ReplyCount
           FROM DiscussionThreads t
           LEFT JOIN Users u         ON t.UserID   = u.UserID
           LEFT JOIN ThreadReplies r ON t.ThreadID = r.ThreadID
           WHERE t.ForumID = %s
           GROUP BY t.ThreadID, t.ForumID, t.UserID, u.Name,
                    t.Title, t.Content, t.CreatedAt
           ORDER BY t.CreatedAt DESC""",
        (forum_id,),
    )


def get_thread_by_id(thread_id: int) -> dict | None:
    """Return a single thread with author name, or None."""
    return query_one(
        """SELECT t.ThreadID, t.ForumID, t.UserID, u.Name AS AuthorName,
                  t.Title, t.Content, t.CreatedAt
           FROM DiscussionThreads t
           LEFT JOIN Users u ON t.UserID = u.UserID
           WHERE t.ThreadID = %s""",
        (thread_id,),
    )


def create_thread(
    forum_id: int,
    user_id: str,
    title: str,
    content: str,
) -> dict | None:
    """Insert a new thread and return the created row."""
    return execute_returning(
        """INSERT INTO DiscussionThreads (ForumID, UserID, Title, Content)
           VALUES (%s, %s, %s, %s)
           RETURNING ThreadID, ForumID, UserID, Title, Content, CreatedAt""",
        (forum_id, user_id, title, content),
    )


# ── Replies ───────────────────────────────────────────────────────────────────

def get_reply_tree(thread_id: int) -> list[dict]:
    """
    Return the full reply tree for a thread using a recursive CTE.
    Rows are ordered depth-first so the frontend can rebuild the tree cheaply.
    """
    return query_all(
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
               LEFT JOIN Users u  ON r.UserID        = u.UserID
               JOIN reply_tree rt ON r.ParentReplyID = rt.ReplyID
           )
           SELECT * FROM reply_tree ORDER BY depth, CreatedAt""",
        (thread_id,),
    )


def get_reply_by_id(reply_id: int) -> dict | None:
    """Return a reply row with its parent ThreadID, or None."""
    return query_one(
        "SELECT ReplyID, ThreadID FROM ThreadReplies WHERE ReplyID = %s",
        (reply_id,),
    )


def create_reply(
    thread_id: int,
    parent_reply_id: int | None,
    user_id: str,
    content: str,
) -> dict | None:
    """Insert a reply (direct or nested) and return the created row."""
    return execute_returning(
        """INSERT INTO ThreadReplies (ThreadID, ParentReplyID, UserID, Content)
           VALUES (%s, %s, %s, %s)
           RETURNING ReplyID, ThreadID, ParentReplyID, UserID, Content, CreatedAt""",
        (thread_id, parent_reply_id, user_id, content),
    )
