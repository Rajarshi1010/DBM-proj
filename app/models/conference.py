from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .user import User

class ConferenceBase(SQLModel):
    title_of_paper: str
    conference_name: str
    held_on: str
    place: str
    isbn: Optional[str] = None


class ConferencePublication(ConferenceBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    faculty_id: int = Field(foreign_key="user.id")
    faculty: "User" = Relationship(back_populates="conferences")

    @property
    def faculty_name(self) -> str:
        return self.faculty.name if self.faculty else "Unknown"

class ConferenceCreate(ConferenceBase):
    faculty_id: Optional[int] = None

class ConferenceUpdate(SQLModel):
    title_of_paper: Optional[str] = None
    conference_name: Optional[str] = None
    held_on: Optional[str] = None
    place: Optional[str] = None
    isbn: Optional[str] = None
    faculty_id: Optional[int] = None

class ConferenceRead(ConferenceBase):
    id: int
    faculty_id: int
    faculty_name: str