# Plan: Add Pydantic API schemas for input validation

## Context
The week2 web app endpoints currently accept `Dict[str, Any]` for request bodies and return `Dict[str, Any]` for responses. Input validation is done manually via `.get()` calls and ad-hoc checks. This refactor introduces Pydantic models as well-defined API contracts for both requests and responses, leveraging FastAPI's native Pydantic integration.

## Files to modify
- `week2/app/routers/action_items.py`
- `week2/app/routers/notes.py`

## Implementation

### 1. `week2/app/routers/action_items.py`

Define Pydantic request/response models and replace `Dict[str, Any]` parameters:

```python
from pydantic import BaseModel, Field

# Request models
class ExtractRequest(BaseModel):
    text: str = Field(..., min_length=1)
    save_note: bool = False

class MarkDoneRequest(BaseModel):
    done: bool = True

# Response models
class ActionItemOut(BaseModel):
    id: int
    text: str

class ExtractResponse(BaseModel):
    note_id: int | None
    items: list[ActionItemOut]

class ActionItemDetail(BaseModel):
    id: int
    note_id: int | None
    text: str
    done: bool
    created_at: str

class MarkDoneResponse(BaseModel):
    id: int
    done: bool
```

Update endpoints to use these models instead of `Dict[str, Any]`.

### 2. `week2/app/routers/notes.py`

```python
from pydantic import BaseModel, Field

# Request models
class CreateNoteRequest(BaseModel):
    content: str = Field(..., min_length=1)

# Response models
class NoteOut(BaseModel):
    id: int
    content: str
    created_at: str
```

Update endpoints to use these models instead of `Dict[str, Any]`.

### Key changes in endpoint signatures
- Remove manual `payload.get()` calls and `HTTPException` for missing fields — Pydantic handles this automatically with 422 validation errors
- Use model field access (`payload.text`) instead of dict access (`payload.get("text")`)
- Add response model type hints for better API documentation

## Verification
1. Run the server: `poetry run uvicorn week2.app.main:app --reload`
2. Test via the frontend at http://127.0.0.1:8000/ — extract action items, toggle done
3. Verify validation errors: `curl -X POST http://127.0.0.1:8000/action-items/extract -H 'Content-Type: application/json' -d '{}'` should return 422
4. Run existing tests: `poetry run pytest week2/tests/`
