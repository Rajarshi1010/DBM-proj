from typing import List, Optional

from pydantic import EmailStr
from sqlmodel import Field, SQLModel, Relationship
import enum

# Define Role Enum
class Role(str, enum.Enum):
    ADMIN = "ADMIN"
    FACULTY = "FACULTY"

# Forward references
class BookPublication(SQLModel): ...
class ConferencePublication(SQLModel): ...
class JournalPublication(SQLModel): ...

# 1. UserBase: Contains fields shared by DB and API (No relationships here!)
class UserBase(SQLModel):
    name: str
    email: EmailStr= Field(unique=True, index=True)
    role: Role = Field(default=Role.FACULTY)
    department: str = "Department of Machine Learning"
    is_active: bool = Field(default=True)

# 2. User: The actual Database Table (Adds ID, Password, and Relationships)
class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str

    # Relationships are ONLY here, in the table definition
    books: List["BookPublication"] = Relationship(back_populates="faculty")
    conferences: List["ConferencePublication"] = Relationship(back_populates="faculty")
    journals: List["JournalPublication"] = Relationship(back_populates="faculty")

class UserUpdate(SQLModel):
    name: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    password: Optional[str] = None # Optional: if they want to change password