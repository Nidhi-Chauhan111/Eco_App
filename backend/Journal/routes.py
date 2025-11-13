# backend/Journal/routes.py

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional

from backend.Journal.journal_service import EcoJournalService
from backend.Auth.deps import get_current_user

router = APIRouter(prefix="/journal", tags=["Eco Journal"])

# Pydantic schema for request - client should NOT send user_id in body
class JournalEntryRequest(BaseModel):
    content: str

# Initialize service
service = EcoJournalService()

# ---------- ROUTES ----------

@router.post("/entry")
def create_journal_entry(entry: JournalEntryRequest, user_id: int = Depends(get_current_user),request: Request = None):
    print("Incoming headers:", dict(request.headers))
    """
    Process and save a journal entry for the logged-in user.
    The user_id comes from the JWT (dependency), not from the client body.

    """
    print(">>> Debug: service object:", repr(service))
    print(">>> Debug: journal_repo on service:", getattr(service, "journal_repo", None))
    try:
        coll = getattr(service, "journal_repo").collection
        print(">>> Debug: journal collection:", coll.name, " db:", coll.database.name)
    except Exception as e:
        print(">>> Debug: cannot resolve collection on service:", repr(e))
    
    result = service.process_journal_entry(user_id, entry.content)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Processing failed"))
    return result


@router.get("/dashboard")
def get_dashboard(user_id: int = Depends(get_current_user)):
    """
    Return dashboard for the authenticated user
    """
    result = service.get_user_dashboard(user_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Dashboard not found"))
    return result


@router.get("/inspiration/{user_id}/{mood}")
def get_inspiration_debug(user_id: int, mood: str):
    print(f">>> Debug: get_inspiration called with user_id={user_id!r}, mood={mood!r}")
    result = service.get_inspiration_for_mood(user_id, mood)
    print(">>> Debug: service.get_inspiration_for_mood returned:", repr(result))
    # return raw result for debugging (be careful in prod)
    return result


@router.get("/entries/{user_id}")
def get_user_entries(user_id: int):
    """
    Get all entries for a user (public)
    """
    result = service.journal_repo.get_user_entries(user_id)
    return {"success": True, "entries": result}


@router.get("/entry/{entry_id}")
def get_entry_by_id(entry_id: str):
    """
    Get single journal entry by ID (public)
    """
    result = service.journal_repo.get_entry_by_id(entry_id)
    if not result:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"success": True, "entry": result}
