# Plan: Database layer cleanup

## Context
The current `week2/app/db.py` has several issues: every function opens a new SQLite connection, `ensure_data_directory_exists()` is called redundantly on every connection, foreign keys are not enforced, and batch inserts use a loop instead of `executemany`. This cleanup consolidates connection management, enables foreign keys, and streamlines the code.

## File to modify
- `week2/app/db.py`

## Changes

### 1. Single shared connection via module-level `_connection`
- Replace per-function `get_connection()` calls with a module-level `_connection` variable
- Introduce `get_connection()` that returns the shared connection (creating it lazily on first call)
- Call `ensure_data_directory_exists()` only once during connection creation, not on every call

### 2. Enable foreign key enforcement
- Add `PRAGMA foreign_keys = ON` after establishing the connection

### 3. Use `executemany` in `insert_action_items`
- Replace the per-item loop with `executemany` for batch inserts
- Use `cursor.lastrowid` with row count to compute all inserted IDs

### 4. Remove redundant code
- Remove the separate `ensure_data_directory_exists()` call from `init_db()` since `get_connection()` already handles it

### Resulting structure
```python
_connection: sqlite3.Connection | None = None

def get_connection() -> sqlite3.Connection:
    global _connection
    if _connection is None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        _connection = sqlite3.connect(DB_PATH)
        _connection.row_factory = sqlite3.Row
        _connection.execute("PRAGMA foreign_keys = ON")
    return _connection

def init_db() -> None:
    conn = get_connection()
    conn.execute("""CREATE TABLE IF NOT EXISTS notes (...)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS action_items (...)""")
    conn.commit()

# All other functions use get_connection() and operate on the shared connection
# insert_action_items uses executemany
```

## Verification
1. Run existing tests: `poetry run pytest week2/tests/ -v`
2. Start server and test via frontend: `poetry run uvicorn week2.app.main:app --reload`
3. Verify foreign key enforcement works (inserting action item with non-existent note_id should fail)
