from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
import enum

if TYPE_CHECKING:
    from .user import User

class JournalType(str, enum.Enum):
    INTERNATIONAL = "International"
    NATIONAL = "National"

class JournalBase(SQLModel):
    title_of_paper: str
    journal_type: JournalType = Field(default=JournalType.INTERNATIONAL)
    journal_name: str
    url_doi: Optional[str] = None
    issn: Optional[str] = None
    publication_month_year: str
    page_numbers: Optional[str] = None


class JournalPublication(JournalBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    faculty_id: int = Field(foreign_key="user.id")
    faculty: "User" = Relationship(back_populates="journals")

    @property
    def faculty_name(self) -> str:
        return self.faculty.name if self.faculty else "Unknown"

class JournalCreate(JournalBase):
    faculty_id: Optional[int] = None

class JournalUpdate(SQLModel):
    title_of_paper: Optional[str] = None
    journal_type: Optional[JournalType] = None
    journal_name: Optional[str] = None
    url_doi: Optional[str] = None
    issn: Optional[str] = None
    publication_month_year: Optional[str] = None
    page_numbers: Optional[str] = None
    faculty_id: Optional[int] = None

class JournalRead(JournalBase):
    id: int
    faculty_id: int
    faculty_name: str