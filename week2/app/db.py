from __future__ import annotations

import sqlite3
from typing import Optional

from .config import DATA_DIR, DB_PATH

_connection: sqlite3.Connection | None = None


def get_connection() -> sqlite3.Connection:
    global _connection
    if _connection is None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        _connection = sqlite3.connect(DB_PATH, check_same_thread=False)
        _connection.row_factory = sqlite3.Row
        _connection.execute("PRAGMA foreign_keys = ON")
    return _connection


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS action_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER,
                text TEXT NOT NULL,
                done INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (note_id) REFERENCES notes(id)
            );
            """
        )


def insert_note(content: str) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notes (content) VALUES (?)", (content,))
        return int(cursor.lastrowid)


def list_notes() -> list[sqlite3.Row]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, content, created_at FROM notes ORDER BY id DESC")
        return list(cursor.fetchall())


def get_note(note_id: int) -> Optional[sqlite3.Row]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, content, created_at FROM notes WHERE id = ?",
            (note_id,),
        )
        return cursor.fetchone()


def insert_action_items(items: list[str], note_id: Optional[int] = None) -> list[int]:
    if not items:
        return []
    with get_connection() as conn:
        cursor = conn.cursor()
        ids: list[int] = []
        for item in items:
            cursor.execute(
                "INSERT INTO action_items (note_id, text) VALUES (?, ?)",
                (note_id, item),
            )
            ids.append(int(cursor.lastrowid))
        return ids


def list_action_items(note_id: Optional[int] = None) -> list[sqlite3.Row]:
    with get_connection() as conn:
        cursor = conn.cursor()
        if note_id is None:
            cursor.execute(
                "SELECT id, note_id, text, done, created_at FROM action_items ORDER BY id DESC"
            )
        else:
            cursor.execute(
                "SELECT id, note_id, text, done, created_at FROM action_items WHERE note_id = ? ORDER BY id DESC",
                (note_id,),
            )
        return list(cursor.fetchall())


def mark_action_item_done(action_item_id: int, done: bool) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE action_items SET done = ? WHERE id = ?",
            (1 if done else 0, action_item_id),
        )
        return cursor.rowcount


def close_connection() -> None:
    global _connection
    if _connection is not None:
        _connection.close()
        _connection = None
