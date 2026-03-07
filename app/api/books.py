from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db.base import get_session
from app.models.book import BookPublication, BookCreate, BookRead, BookUpdate
from app.models.user import User, Role
from app.api.auth import get_current_user

router = APIRouter()


# Input: BookCreate (No ID), Output: BookRead (With ID)
@router.post("/", response_model=BookRead)
def create_book(
        book_in: BookCreate,  # <--- CHANGED THIS
        current_user: Annotated[User, Depends(get_current_user)],
        session: Session = Depends(get_session)
):
    # 1. Dump data (excluding faculty_id initially)
    data = book_in.model_dump(exclude={"faculty_id"})
    book_db = BookPublication(**data)

    # 2. Permission Logic
    if current_user.role == Role.FACULTY:
        # Force the book to belong to the logged-in user
        book_db.faculty_id = current_user.id

    elif current_user.role == Role.ADMIN:        # Admins must specify which faculty to assign the book to
        if not book_in.faculty_id:
            raise HTTPException(status_code=400, detail="Admins must provide 'faculty_id' to assign the book.")
        if not session.get(User, book_in.faculty_id):
            raise HTTPException(status_code=404, detail="Target faculty ID not found")
        book_db.faculty_id = book_in.faculty_id

    session.add(book_db)
    session.commit()
    session.refresh(book_db)
    return book_db

@router.patch("/{book_id}", response_model=BookRead)
def update_book(
    book_id: int,
    book_in: BookUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session)
):
    # 1. Fetch the book
    db_book = session.get(BookPublication, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book entry not found")

    # 2. Authorization: Admin or Owner?
    if current_user.role != Role.ADMIN and db_book.faculty_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this book")

    # 3. Dump data excluding unset fields
    update_data = book_in.model_dump(exclude_unset=True)

    # 4. Handle faculty_id reassignment
    if "faculty_id" in update_data:
        if current_user.role == Role.ADMIN:
            if not session.get(User, update_data["faculty_id"]):
                raise HTTPException(status_code=404, detail="Target faculty not found")
        else:
            # Silently prevent non-admins from changing ownership
            del update_data["faculty_id"]

    # 5. Apply and Commit
    for key, value in update_data.items():
        setattr(db_book, key, value)

    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book

@router.get("/", response_model=List[BookRead])
def list_books(
        faculty_id: int | None = None,
        session: Session = Depends(get_session)
):
    query = select(BookPublication)
    if faculty_id:
        query = query.where(BookPublication.faculty_id == faculty_id)
    return session.exec(query).all()


@router.delete("/{book_id}")
def delete_book(
        book_id: int,
        current_user: Annotated[User, Depends(get_current_user)],
        session: Session = Depends(get_session)
):
    book = session.get(BookPublication, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if current_user.role != Role.ADMIN and book.faculty_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    session.delete(book)
    session.commit()
    return {"ok": True}