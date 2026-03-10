from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.base import get_session
from app.models.journal import JournalPublication, JournalCreate, JournalRead, JournalUpdate
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

@router.patch("/{journal_id}", response_model=JournalRead)
def update_journal(
    journal_id: int,
    journal_in: JournalUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session)
):
    # 1. Fetch existing record
    db_journal = session.get(JournalPublication, journal_id)
    if not db_journal:
        raise HTTPException(status_code=404, detail="Journal entry not found")

    # 2. Permission Check
    if current_user.role != Role.ADMIN and db_journal.faculty_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this entry")

    # 3. Process data (exclude_unset=True is key for PATCH)
    update_data = journal_in.model_dump(exclude_unset=True)

    # 4. Handle faculty_id reassignment logic
    if "faculty_id" in update_data:
        if current_user.role == Role.ADMIN:
            # Verify new owner exists
            if not session.get(User, update_data["faculty_id"]):
                raise HTTPException(status_code=404, detail="New faculty owner not found")
        else:
            # Faculty cannot change the owner, even to themselves (redundant but safe)
            del update_data["faculty_id"]

    # 5. Apply updates and commit
    for key, value in update_data.items():
        setattr(db_journal, key, value)

    session.add(db_journal)
    session.commit()
    session.refresh(db_journal)
    return db_journal


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