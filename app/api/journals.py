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
    data = journal_in.model_dump(exclude={"faculty_id"})
    journal_db = JournalPublication(**data)

    if current_user.role == Role.FACULTY:
        journal_db.faculty_id = current_user.id
    elif current_user.role == Role.ADMIN:
        if not journal_in.faculty_id:
            raise HTTPException(status_code=400, detail="Admins must provide 'faculty_id'.")
        if not session.get(User, journal_in.faculty_id):
            raise HTTPException(status_code=404, detail="Target faculty not found")
        journal_db.faculty_id = journal_in.faculty_id

    session.add(journal_db)
    session.commit()
    session.refresh(journal_db)
    return journal_db


@router.get("/", response_model=List[JournalRead])
def list_journals(faculty_id: int | None = None, session: Session = Depends(get_session)):
    query = select(JournalPublication)
    if faculty_id: query = query.where(JournalPublication.faculty_id == faculty_id)
    return session.exec(query).all()


@router.delete("/{journal_id}")
def delete_journal(
        journal_id: int,
        current_user: Annotated[User, Depends(get_current_user)],
        session: Session = Depends(get_session)
):
    journal = session.get(JournalPublication, journal_id)
    if not journal:
        raise HTTPException(status_code=404, detail="Journal paper not found")
    if current_user.role != Role.ADMIN and journal.faculty_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this entry")
    session.delete(journal)
    session.commit()
    return {"ok": True}