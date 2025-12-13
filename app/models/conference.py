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
    faculty_id: int = Field(foreign_key="user.id")

class ConferencePublication(ConferenceBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    faculty: "User" = Relationship(back_populates="conferences")

    @property
    def faculty_name(self) -> str:
        return self.faculty.name if self.faculty else "Unknown"

class ConferenceCreate(ConferenceBase):
    pass

class ConferenceRead(ConferenceBase):
    id: int