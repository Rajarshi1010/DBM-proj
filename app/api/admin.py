from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.db.base import get_session
from app.models.user import User, UserBase, Role
from app.models.book import BookPublication
from app.models.conference import ConferencePublication
from app.models.journal import JournalPublication
from app.core.security import get_password_hash
from app.api.auth import get_current_user

router = APIRouter()


def get_current_admin(user: Annotated[User, Depends(get_current_user)]) -> User:
    """
    Custom dependency that ensures the user is an ADMIN.
    If a normal FACULTY tries to access these endpoints, they get a 403 Forbidden.
    """
    if user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have admin privileges"
        )
    return user


class FacultyCreate(UserBase):
    password: str


class FacultyUpdate(UserBase):
    # All fields optional for updates
    name: str | None = None
    email: str | None = None
    department: str | None = None
    role: Role | None = None
    is_active: bool | None = None
    password: str | None = None

@router.post("/faculty", response_model=UserBase)
def create_faculty_account(
        faculty_in: FacultyCreate,
        current_admin: Annotated[User, Depends(get_current_admin)],
        session: Session = Depends(get_session)
):
    """
    Admin only: Create a new faculty account.
    """
    existing_user = session.exec(select(User).where(User.email == faculty_in.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pwd = get_password_hash(faculty_in.password)
    db_user = User(
        **faculty_in.model_dump(exclude={"password"}),
        hashed_password=hashed_pwd
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.patch("/faculty/{user_id}", response_model=User) # Return full User, not just Base
def update_faculty_account(
        user_id: int,
        faculty_update: FacultyUpdate,
        session: Session = Depends(get_session)
):
    """
    Admin only: Update a faculty account (change role, deactivate, reset password).
    """
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = faculty_update.model_dump(exclude_unset=True)

    if "password" in update_data and update_data["password"]:
        password = update_data.pop("password")
        db_user.hashed_password = get_password_hash(password)
    db_user.sqlmodel_update(update_data)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.delete("/users/{user_id}")
def delete_faculty(
        user_id: int,
        current_admin: Annotated[User, Depends(get_current_admin)],
        session: Session = Depends(get_session)
):
    """
    Admin Only: Delete a user (Faculty or Admin).
    Also deletes all their linked Books, Conferences, and Journals.
    Prevents admin from deleting themselves.
    """
    if user_id == current_admin.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot delete your own account."
        )
    user_to_delete = session.get(User, user_id)
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="User not found")


    books = session.exec(select(BookPublication).where(BookPublication.faculty_id == user_id)).all()
    for book in books:
        session.delete(book)

    confs = session.exec(select(ConferencePublication).where(ConferencePublication.faculty_id == user_id)).all()
    for conf in confs:
        session.delete(conf)

    journals = session.exec(select(JournalPublication).where(JournalPublication.faculty_id == user_id)).all()
    for journal in journals:
        session.delete(journal)

    session.delete(user_to_delete)
    session.commit()

    return {
        "ok": True,
        "message": f"User '{user_to_delete.name}' and all linked publications deleted successfully."
    }