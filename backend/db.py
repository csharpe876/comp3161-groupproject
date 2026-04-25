"""
Database connection pool and query helpers.
All queries use parameterised placeholders (%s) to prevent SQL injection.
"""
from __future__ import annotations

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

from config import Config

_pool: pool.ThreadedConnectionPool | None = None


def init_pool() -> None:
    global _pool
    _pool = pool.ThreadedConnectionPool(
        minconn=2,
        maxconn=20,
        dsn=Config.DATABASE_URL,
    )


def _get_pool() -> pool.ThreadedConnectionPool:
    if _pool is None:
        raise RuntimeError("Database pool not initialised. Call init_pool() first.")
    return _pool


class _Conn:
    """Context manager: acquires a connection, commits on success, rolls back on error."""

    def __enter__(self) -> psycopg2.extensions.connection:
        self.conn = _get_pool().getconn()
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.conn.rollback()
        else:
            self.conn.commit()
        _get_pool().putconn(self.conn)
        return False  # propagate exceptions


def query_one(sql: str, params=None):
    """Return the first row as a dict, or None."""
    with _Conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
            return dict(row) if row else None


def query_all(sql: str, params=None) -> list[dict]:
    """Return all rows as a list of dicts."""
    with _Conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
            return [dict(r) for r in rows] if rows else []


def execute(sql: str, params=None) -> int:
    """Execute a non-SELECT statement and return the affected row count."""
    with _Conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.rowcount


def execute_returning(sql: str, params=None) -> dict | None:
    """Execute a statement with a RETURNING clause and return the first row."""
    with _Conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
            return dict(row) if row else None
