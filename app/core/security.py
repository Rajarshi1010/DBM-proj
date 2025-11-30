from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

# Setup password hashing (using Bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 1. Hash a password (turn "secret" into "$2b$12$...")
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# 2. Verify a password (check if input matches the hash)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# 3. Create the JWT Token (The Key Card)
def create_access_token(subject: Union[str, Any], role: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # The "Payload" contains the User ID (sub) and their Role
    to_encode = {"exp": expire, "sub": str(subject), "role": role}

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt