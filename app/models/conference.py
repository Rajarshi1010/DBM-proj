from typing import Optional
from sqlmodel import Field, SQLModel, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User


class ConferencePublication(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    title_of_paper: str
    conference_name: str
    held_on: str
    place: str
    isbn: Optional[str] = None

    # Foreign Key
    faculty_id: int = Field(foreign_key="user.id")
    faculty: "User" = Relationship(back_populates="conferences")