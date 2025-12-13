from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from sqlmodel import Session, select

from app.db.base import get_session
from app.core.config import settings
from app.core.security import verify_password, create_access_token, get_password_hash
from app.models.user import User, UserUpdate

# This tells FastAPI that the client should send the token in the "Authorization" header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter()
async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        session: Annotated[Session, Depends(get_session)]
) -> User:
    """
    Validates the token. If valid, fetches the User from DB.
    If invalid, kicks them out (401 Unauthorized).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the token using our SECRET_KEY
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = session.get(User, int(user_id))
    if user is None:
        raise credentials_exception
    return user


@router.post("/login")
def login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        session: Annotated[Session, Depends(get_session)]
):
    statement = select(User).where(User.email == form_data.username)
    user = session.exec(statement).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=user.id, role=user.role.value)

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/setup-admin")
def create_initial_admin(session: Annotated[Session, Depends(get_session)]):
    """Temporary endpoint to create your first Admin user"""
    stmt = select(User).where(User.email == "admin@bmsce.ac.in")
    if session.exec(stmt).first():
        return {"message": "Admin already exists"}

    admin_user = User(
        name="System Admin",
        email="admin@bmsce.ac.in",
        hashed_password=get_password_hash("admin123"),
        role="ADMIN",
        department="Administration"
    )
    session.add(admin_user)
    session.commit()
    return {"message": "Admin created! Login with email: admin@bmsce.ac.in / pass: admin123"}


@router.put("/me", response_model=User)
def update_my_profile(
        update_data: UserUpdate,
        current_user: Annotated[User, Depends(get_current_user)],
        session: Session = Depends(get_session)
):
    """
    Update the logged-in user's profile.
    No 'user_id' needed in URL because 'current_user' COMES from the token.
    """
    # 1. Update basic fields
    if update_data.name:
        current_user.name = update_data.name
    if update_data.email:
        current_user.email = update_data.email
    if update_data.department:
        current_user.department = update_data.department

    # 2. Handle Password Change (Hash it first!)
    if update_data.password:
        current_user.hashed_password = get_password_hash(update_data.password)

    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user