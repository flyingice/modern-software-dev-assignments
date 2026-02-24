# Action Item Extractor

A FastAPI web application that extracts action items from free-form notes using either heuristic pattern matching or LLM-powered extraction via Ollama.

## Tech Stack

- **FastAPI** — web framework and API layer
- **SQLite** — data persistence (notes and action items)
- **Ollama** — local LLM inference (llama3.1:8b)
- **Pydantic** — request/response validation
- **Uvicorn** — ASGI server

## Project Structure

```
week2/
├── app/
│   ├── config.py              # Environment-based configuration
│   ├── db.py                  # SQLite database layer
│   ├── main.py                # FastAPI app setup and lifespan
│   ├── routers/
│   │   ├── action_items.py    # /action-items endpoints
│   │   └── notes.py           # /notes endpoints
│   └── services/
│       └── extract.py         # Heuristic and LLM extraction logic
├── frontend/
│   └── index.html             # Single-page web UI
├── tests/
│   ├── test_extract.py        # Unit tests for extraction functions
│   └── test_error_handling.py # HTTP error handling tests
└── data/
    └── app.db                 # SQLite database (auto-created)
```

## Setup

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/) running locally with the `llama3.1:8b` model pulled

```bash
ollama pull llama3.1:8b
```

### Install Dependencies

```bash
poetry install
```

### Configuration

The following environment variables can be set (all have sensible defaults):

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_DATA_DIR` | `week2/data/` | Directory for the SQLite database |
| `APP_DB_PATH` | `week2/data/app.db` | Full path to the database file |
| `APP_OLLAMA_MODEL` | `llama3.1:8b` | Ollama model used for LLM extraction |

## Running the App

```bash
poetry run uvicorn week2.app.main:app --reload
```

Open http://127.0.0.1:8000/ in a browser.

## Running Tests

```bash
cd week2 && python -m pytest tests/ -v
```

> **Note:** Tests for LLM extraction call Ollama directly (not mocked), so the Ollama service must be running.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serves the web UI |
| `POST` | `/action-items/extract` | Extract action items using heuristic rules |
| `POST` | `/action-items/extract-llm` | Extract action items using LLM |
| `GET` | `/action-items` | List all action items (optional `?note_id=` filter) |
| `POST` | `/action-items/{id}/done` | Mark an action item as done/undone |
| `POST` | `/notes` | Create a note |
| `GET` | `/notes` | List all notes |
| `GET` | `/notes/{id}` | Get a single note |

## Database Schema

**notes**

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key (auto-increment) |
| `content` | TEXT | Note content |
| `created_at` | TEXT | Timestamp (auto-set) |

**action_items**

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key (auto-increment) |
| `note_id` | INTEGER | Foreign key to notes (nullable) |
| `text` | TEXT | Action item text |
| `done` | INTEGER | Completion flag (0/1) |
| `created_at` | TEXT | Timestamp (auto-set) |
