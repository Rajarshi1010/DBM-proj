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
    # Faculty ID is needed to link the book, but we validate it in the API
    faculty_id: int = Field(foreign_key="user.id")

# 2. Table Model: The actual DB table (Adds ID & Relationship)
class BookPublication(BookBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    faculty: "User" = Relationship(back_populates="books")

# 3. Create Schema: What the User sends (Strictly NO ID allowed)
class BookCreate(BookBase):
    pass

# 4. Read Schema: What the API returns (Includes ID)
class BookRead(BookBase):
    id: int