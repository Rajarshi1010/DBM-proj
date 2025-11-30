from typing import Optional
from sqlmodel import Field, SQLModel, Relationship
from typing import TYPE_CHECKING
import enum

if TYPE_CHECKING:
    from .user import User


class JournalType(str, enum.Enum):
    INTERNATIONAL = "International"
    NATIONAL = "National"


class JournalPublication(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    title_of_paper: str
    journal_type: JournalType = Field(default=JournalType.INTERNATIONAL)
    journal_name: str
    url_doi: Optional[str] = None
    issn: Optional[str] = None
    publication_month_year: str
    page_numbers: Optional[str] = None

    # Foreign Key
    faculty_id: int = Field(foreign_key="user.id")
    faculty: "User" = Relationship(back_populates="journals")