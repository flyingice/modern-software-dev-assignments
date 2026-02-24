# Plan: Add LLM Extraction Endpoint, List Notes Endpoint, and Frontend Buttons

## Context
The week2 app already has `extract_action_items_llm()` in `app/services/extract.py` and `db.list_notes()` in `app/db.py`, but neither is wired to an HTTP endpoint. The existing `/action-items/extract` endpoint only uses the heuristic `extract_action_items()`. We need to expose both capabilities via new endpoints and add corresponding UI buttons.

## Changes

### 1. Add LLM extraction endpoint — `week2/app/routers/action_items.py`
- Import `extract_action_items_llm` and `OllamaServiceError` from `..services.extract`
- Add `POST /action-items/extract-llm` endpoint (mirrors existing `/extract` pattern):
  - Accepts same `ExtractRequest` body (`text`, `save_note`)
  - Calls `extract_action_items_llm(text)` instead of `extract_action_items(text)`
  - Saves note if `save_note` is true (same logic as existing endpoint)
  - Inserts action items into DB, returns `ExtractResponse`
  - Catches `OllamaServiceError` → returns HTTP 503

### 2. Add list-all-notes endpoint — `week2/app/routers/notes.py`
- Currently has: `POST /notes` (create) and `GET /notes/{note_id}` (get single) — no list endpoint exists
- Add `GET /notes` endpoint (no path parameter, distinct from `GET /notes/{note_id}`):
  - Calls existing `db.list_notes()`
  - Returns `list[NoteOut]`

### 3. Update frontend — `week2/frontend/index.html`
- Add "Extract LLM" button next to existing "Extract" button in the `.row` div
- Add click handler that POSTs to `/action-items/extract-llm` (same payload/response handling as existing Extract button)
- Add "List Notes" button (separate section below the controls)
- Add a `<div id="notes">` container for displaying notes
- Add click handler that GETs `/notes` and renders each note (id, content snippet, created_at)

## Files to Modify
- `week2/app/routers/action_items.py` — new LLM extract endpoint
- `week2/app/routers/notes.py` — new list notes endpoint
- `week2/frontend/index.html` — two new buttons + handlers

## Verification
1. Run existing tests: `cd week2 && python -m pytest tests/`
2. Start the app and test manually:
   - Click "Extract LLM" with sample text → should return LLM-extracted items (requires Ollama running)
   - Click "List Notes" → should display all saved notes
3. Test error cases: "Extract LLM" when Ollama is down should show an error message
