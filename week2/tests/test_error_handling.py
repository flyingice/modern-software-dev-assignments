import sqlite3
from unittest.mock import patch

from fastapi.testclient import TestClient

from ..app.main import app
from ..app import db as db_module


def _setup_test_db():
    """Set up an in-memory SQLite database for testing."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute(
        """
        CREATE TABLE notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE action_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id INTEGER,
            text TEXT NOT NULL,
            done INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (note_id) REFERENCES notes(id)
        )
        """
    )
    return conn


@patch.object(db_module, "_connection", None)
def test_mark_done_nonexistent_item_returns_404():
    conn = _setup_test_db()
    with patch.object(db_module, "get_connection", return_value=conn):
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.post("/action-items/9999/done", json={"done": True})
        assert resp.status_code == 404
        assert "action item not found" in resp.json()["detail"]


@patch.object(db_module, "_connection", None)
def test_get_nonexistent_note_returns_404():
    conn = _setup_test_db()
    with patch.object(db_module, "get_connection", return_value=conn):
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/notes/9999")
        assert resp.status_code == 404
        assert "note not found" in resp.json()["detail"]


def test_extract_empty_text_returns_422():
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.post("/action-items/extract", json={"text": ""})
    assert resp.status_code == 422


@patch.object(db_module, "_connection", None)
def test_db_error_returns_500():
    with patch.object(
        db_module,
        "get_connection",
        side_effect=sqlite3.OperationalError("disk I/O error"),
    ):
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/notes/1")
        assert resp.status_code == 500
        assert resp.json()["detail"] == "Internal server error"
