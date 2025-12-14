from typing import Optional
from sqlmodel import Field, SQLModel, Relationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User


# 1. Base Class: Fields shared by everything
class BookBase(SQLModel):
    title: str
    publisher_details: str
    publication_month_year: str


# 2. Table Model: The actual DB table (Adds ID & Relationship)
class BookPublication(BookBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    faculty_id: int = Field(foreign_key="user.id")  # Foreign Key is here
    faculty: "User" = Relationship(back_populates="books")

    @property
    def faculty_name(self) -> str:
        return self.faculty.name if self.faculty else "Unknown"

# 3. Create Schema: What the User sends (Strictly NO ID allowed)
class BookCreate(BookBase):
    # Optional: Admins can use this. Faculty don't need to.
    faculty_id: Optional[int] = None

# 4. Read Schema: What the API returns (Includes ID)
class BookRead(BookBase):
    id: int
    faculty_id: int
    faculty_name: str