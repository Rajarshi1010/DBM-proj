from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.db.base import get_session
from app.models.user import User, Role,UserBase

router = APIRouter()

# --- Response Models (Schemas) ---
# We define these here to control what data is sent back (hiding passwords)
# In a larger app, these go into a 'schemas' folder.
from app.models.book import BookPublication
from app.models.conference import ConferencePublication
from app.models.journal import JournalPublication

class UserPublic(UserBase):
    id: int # We explicitly add ID because UserBase doesn't have it, This class safely ignores 'books', 'hashed_password', etc.


class UserProfile(UserPublic):
    # This is the "Full Profile" view including relationships
    books: List[BookPublication] = []
    conferences: List[ConferencePublication] = []
    journals: List[JournalPublication] = []

# --- Endpoints ---

@router.get("/", response_model=List[UserPublic], response_model_exclude={"hashed_password"})
def list_faculty(session: Session = Depends(get_session)):
    """List all Faculty members (excludes Admins)."""
    statement = select(User).where(User.role == Role.FACULTY)
    faculty_list = session.exec(statement).all()
    return faculty_list

@router.get("/{user_id}", response_model=UserProfile, response_model_exclude={"hashed_password"})
def get_faculty_profile(user_id: int, session: Session = Depends(get_session)):
    """
    Get a single faculty's profile + ALL their publications.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Faculty not found")
    return user