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
    faculty_id: int = Field(foreign_key="user.id")

class JournalPublication(JournalBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    faculty: "User" = Relationship(back_populates="journals")

    @property
    def faculty_name(self) -> str:
        return self.faculty.name if self.faculty else "Unknown"

class JournalCreate(JournalBase):
    pass

class JournalRead(JournalBase):
    id: int