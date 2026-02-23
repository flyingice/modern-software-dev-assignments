# Plan: Application lifecycle management and configuration

## Context
Currently `init_db()` runs at module import time (not tied to FastAPI's lifecycle), the shared DB connection is never closed on shutdown, and configuration values (DB path, model name) are hardcoded with no way to override them for testing or different environments.

## Files to modify
- `week2/app/config.py` — **new file**
- `week2/app/db.py` — import config, add `close_connection()`
- `week2/app/main.py` — add lifespan context manager
- `week2/app/services/extract.py` — use config for model name

---

### 1. Create `week2/app/config.py`
Centralize configuration using `os.environ.get()` with sensible defaults. Move `load_dotenv()` here so `.env` is loaded once before any config is read.

```python
from dotenv import load_dotenv
load_dotenv()

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = Path(os.environ.get("APP_DATA_DIR", str(BASE_DIR / "data")))
DB_PATH = Path(os.environ.get("APP_DB_PATH", str(DATA_DIR / "app.db")))
OLLAMA_MODEL = os.environ.get("APP_OLLAMA_MODEL", "llama3.1:8b")
```

### 2. Update `week2/app/db.py`
- Replace the 3 hardcoded path lines (`BASE_DIR`, `DATA_DIR`, `DB_PATH`) with `from .config import DATA_DIR, DB_PATH`
- Add `close_connection()` to cleanly close and reset the shared connection:
  ```python
  def close_connection() -> None:
      global _connection
      if _connection is not None:
          _connection.close()
          _connection = None
  ```

### 3. Update `week2/app/main.py`
Replace the bare `init_db()` call at import time with a FastAPI lifespan context manager:

```python
from contextlib import asynccontextmanager
from .db import init_db, close_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    close_connection()

app = FastAPI(title="Action Item Extractor", lifespan=lifespan)
```

Remove the `init_db()` call on line 14.

### 4. Update `week2/app/services/extract.py`
- Import `OLLAMA_MODEL` from config: `from ..config import OLLAMA_MODEL`
- Replace hardcoded `model="llama3.1:8b"` with `model=OLLAMA_MODEL`
- Remove the local `load_dotenv()` import and call (now handled by config)

## Verification
1. `poetry run pytest week2/tests/ -v` — existing tests should pass
2. `poetry run uvicorn week2.app.main:app --reload` — start server and test via frontend
3. Verify env var override works: `APP_DB_PATH=/tmp/test.db poetry run uvicorn week2.app.main:app`
