from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .. import db


# Request models
class CreateNoteRequest(BaseModel):
    content: str = Field(..., min_length=1)


# Response models
class NoteOut(BaseModel):
    id: int
    content: str
    created_at: str


router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("")
def create_note(payload: CreateNoteRequest) -> NoteOut:
    note_id = db.insert_note(payload.content.strip())
    note = db.get_note(note_id)
    return NoteOut(
        id=note["id"],
        content=note["content"],
        created_at=note["created_at"],
    )


@router.get("/{note_id}")
def get_single_note(note_id: int) -> NoteOut:
    row = db.get_note(note_id)
    if row is None:
        raise HTTPException(status_code=404, detail="note not found")
    return NoteOut(id=row["id"], content=row["content"], created_at=row["created_at"])
