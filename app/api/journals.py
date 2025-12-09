from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.base import get_session
from app.models.journal import JournalPublication, JournalCreate, JournalRead
from app.models.user import User, Role
from app.api.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=JournalRead)
def create_journal(
    journal_in: JournalCreate, # <--- CHANGED
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session)
):
    journal_db = JournalPublication(**journal_in.model_dump())

    if current_user.role == Role.FACULTY:
        journal_db.faculty_id = current_user.id
    elif current_user.role == Role.ADMIN:
        if not session.get(User, journal_db.faculty_id):
             raise HTTPException(status_code=404, detail="Target faculty ID not found")

    session.add(journal_db)
    session.commit()
    session.refresh(journal_db)
    return journal_db

# (List and Delete endpoints follow the same pattern)
@router.get("/", response_model=List[JournalRead])
def list_journals(faculty_id: int | None = None, session: Session = Depends(get_session)):
    query = select(JournalPublication)
    if faculty_id: query = query.where(JournalPublication.faculty_id == faculty_id)
    return session.exec(query).all()