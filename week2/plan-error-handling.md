# Plan: Comprehensive Error Handling

## Context
The application has no error handling beyond a single 404 check in `GET /notes/{note_id}`. Ollama calls can fail silently with opaque 500s, `mark_done` silently succeeds on nonexistent IDs, and DB infrastructure errors produce raw tracebacks. We'll add layered error handling: service → routes → global handler, plus tests.

## Files to modify (in order)

### 1. `week2/app/services/extract.py` — Ollama error handling
- Add `import logging` and `from pydantic import ValidationError`
- Import `RequestError, ResponseError` from `ollama`
- Define `OllamaServiceError(Exception)` custom exception
- In `extract_action_items_llm()`:
  - Wrap `chat()` call in try/except catching `RequestError` (server unreachable) and `ResponseError` (model not found, server error) → re-raise as `OllamaServiceError`
  - Wrap `ActionItems.model_validate_json()` in try/except catching `ValidationError` → re-raise as `OllamaServiceError`
  - Log at ERROR level before re-raising

### 2. `week2/app/db.py` — `mark_action_item_done` returns row count
- Change return type from `None` to `int`
- Use `cursor = conn.cursor()` + `cursor.execute(...)` + `return cursor.rowcount`
- No other changes in db.py — SQLite infrastructure errors (disk full, locked) are truly exceptional and will be caught by the global handler

### 3. `week2/app/routers/action_items.py` — route-level checks
- Import `HTTPException` from fastapi
- `mark_done`: check `rows_affected == 0` → raise `HTTPException(404, "action item not found")`
- Note: `extract` endpoint currently calls `extract_action_items` (regex-only, no Ollama), so no `OllamaServiceError` catch needed yet. It would become needed when the route switches to `extract_action_items_llm`.

### 4. `week2/app/main.py` — global exception handlers
- Add `import logging` and create logger
- Add `@app.exception_handler(Exception)` that logs the exception and returns `JSONResponse(500, {"detail": "Internal server error"})`. This catches unexpected DB errors, runtime errors, etc. without leaking tracebacks.
- Add `@app.exception_handler(OllamaServiceError)` as a safety net returning `JSONResponse(503, {"detail": str(exc)})` — catches any unhandled Ollama errors from future routes.

### 5. `week2/tests/test_extract.py` — service-layer error tests
Add 3 tests using `unittest.mock.patch` and `pytest.raises`:
- `test_extract_action_items_llm_ollama_unreachable` — mock `chat` to raise `RequestError`, assert `OllamaServiceError`
- `test_extract_action_items_llm_ollama_model_error` — mock `chat` to raise `ResponseError`, assert `OllamaServiceError`
- `test_extract_action_items_llm_malformed_response` — mock `chat` to return invalid JSON content, assert `OllamaServiceError`

### 6. `week2/tests/test_error_handling.py` — new file, API-level error tests
Using `TestClient` with a patched in-memory DB:
- `test_mark_done_nonexistent_item_returns_404`
- `test_get_nonexistent_note_returns_404` (regression test)
- `test_extract_empty_text_returns_422` (regression test)
- `test_db_error_returns_500` — mock a DB function to raise `sqlite3.OperationalError`, verify generic 500

## Error → HTTP status mapping

| Scenario | Status | Detail |
|---|---|---|
| Ollama unreachable / model error / bad output | 503 | Descriptive message |
| Nonexistent note or action item | 404 | "note not found" / "action item not found" |
| DB infrastructure failure | 500 | "Internal server error" (no traceback leak) |
| Invalid request body | 422 | Pydantic validation (already handled by FastAPI) |

## Verification
1. `poetry run pytest week2/tests/ -v` — all existing + new tests pass
2. Manual: stop Ollama, call extract endpoint → should get 503 not 500
3. Manual: `POST /action-items/9999/done` → should get 404 not 200
