from typing import Optional
from sqlmodel import Field, SQLModel, Relationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User


class BookPublication(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    title: str
    publisher_details: str
    publication_month_year: str

    # Foreign Key to Faculty
    faculty_id: int = Field(foreign_key="user.id")
    faculty: "User" = Relationship(back_populates="books")