from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db.base import get_session
from app.models.journal import JournalPublication
from app.models.user import User, Role
from app.api.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=JournalPublication)
def create_journal(
    journal: JournalPublication,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session)
):
    """Create a new Journal Article."""
    if current_user.role == Role.FACULTY:
        journal.faculty_id = current_user.id
    elif current_user.role == Role.ADMIN:
        if not session.get(User, journal.faculty_id):
             raise HTTPException(status_code=404, detail="Target faculty ID not found")

    session.add(journal)
    session.commit()
    session.refresh(journal)
    return journal

@router.get("/", response_model=List[JournalPublication])
def list_journals(
    faculty_id: int | None = None,
    session: Session = Depends(get_session)
):
    """List journals, optionally filtered by faculty_id."""
    query = select(JournalPublication)
    if faculty_id:
        query = query.where(JournalPublication.faculty_id == faculty_id)
    return session.exec(query).all()

@router.delete("/{id}")
def delete_journal(
    id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session)
):
    """Delete a journal article."""
    journal = session.get(JournalPublication, id)
    if not journal:
        raise HTTPException(status_code=404, detail="Journal not found")

    if current_user.role != Role.ADMIN and journal.faculty_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    session.delete(journal)
    session.commit()
    return {"ok": True}