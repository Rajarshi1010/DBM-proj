from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db.base import get_session
from app.models.user import User, UserBase, Role, UserUpdate
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
    password: str # Plaintext password for account creation


class FacultyUpdate(UserBase):
    # All fields optional for updates
    name: str | None = None
    email: str | None = None
    department: str | None = None
    role: Role | None = None
    is_active: bool | None = None
    password: str | None = None  # Optional password reset

@router.post("/faculty", response_model=UserBase)
def create_faculty_account(
        faculty_in: FacultyCreate,
        current_admin: Annotated[User, Depends(get_current_admin)],
        session: Session = Depends(get_session)
):
    """
    Admin only: Create a new faculty account.
    """
    # 1. Check if email already exists
    existing_user = session.exec(select(User).where(User.email == faculty_in.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 2. Hash the password
    hashed_pwd = get_password_hash(faculty_in.password)

    # 3. Create DB Object
    # We use model_dump to extract fields from UserBase (name, email, role, etc.)
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
        faculty_update: FacultyUpdate, # Ensure this schema has all fields Optional
        current_admin: Annotated[User, Depends(get_current_admin)],
        session: Session = Depends(get_session)
):
    """
    Admin only: Update a faculty account (change role, deactivate, reset password).
    """
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # 1. Prepare data (exclude empty fields)
    update_data = faculty_update.model_dump(exclude_unset=True)

    # 2. Handle Password Hashing
    if "password" in update_data and update_data["password"]:
        password = update_data.pop("password")
        db_user.hashed_password = get_password_hash(password)

    # 3. Clean Update (Replaces your 'for' loop)
    db_user.sqlmodel_update(update_data)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user