from __future__ import annotations

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from .. import db
from ..services.extract import extract_action_items


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


router = APIRouter(prefix="/action-items", tags=["action-items"])


@router.post("/extract")
def extract(payload: ExtractRequest) -> ExtractResponse:
    text = payload.text.strip()

    note_id: int | None = None
    if payload.save_note:
        note_id = db.insert_note(text)

    items = extract_action_items(text)
    ids = db.insert_action_items(items, note_id=note_id)
    return ExtractResponse(
        note_id=note_id,
        items=[ActionItemOut(id=i, text=t) for i, t in zip(ids, items)],
    )


@router.get("")
def list_all(note_id: Optional[int] = None) -> list[ActionItemDetail]:
    rows = db.list_action_items(note_id=note_id)
    return [
        ActionItemDetail(
            id=r["id"],
            note_id=r["note_id"],
            text=r["text"],
            done=bool(r["done"]),
            created_at=r["created_at"],
        )
        for r in rows
    ]


@router.post("/{action_item_id}/done")
def mark_done(action_item_id: int, payload: MarkDoneRequest) -> MarkDoneResponse:
    db.mark_action_item_done(action_item_id, payload.done)
    return MarkDoneResponse(id=action_item_id, done=payload.done)
