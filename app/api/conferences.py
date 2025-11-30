from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db.base import get_session
from app.models.conference import ConferencePublication
from app.models.user import User, Role
from app.api.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=ConferencePublication)
def create_conference(
    conference: ConferencePublication,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session)
):
    """Create a new Conference Paper."""
    if current_user.role == Role.FACULTY:
        conference.faculty_id = current_user.id
    elif current_user.role == Role.ADMIN:
        if not session.get(User, conference.faculty_id):
             raise HTTPException(status_code=404, detail="Target faculty ID not found")

    session.add(conference)
    session.commit()
    session.refresh(conference)
    return conference

@router.get("/", response_model=List[ConferencePublication])
def list_conferences(
    faculty_id: int | None = None,
    session: Session = Depends(get_session)
):
    """List conferences, optionally filtered by faculty_id."""
    query = select(ConferencePublication)
    if faculty_id:
        query = query.where(ConferencePublication.faculty_id == faculty_id)
    return session.exec(query).all()

@router.delete("/{id}")
def delete_conference(
    id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session)
):
    """Delete a conference paper."""
    conf = session.get(ConferencePublication, id)
    if not conf:
        raise HTTPException(status_code=404, detail="Conference paper not found")

    if current_user.role != Role.ADMIN and conf.faculty_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    session.delete(conf)
    session.commit()
    return {"ok": True}