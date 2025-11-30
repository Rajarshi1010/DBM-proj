from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db.base import get_session
from app.models.book import BookPublication
from app.models.user import User, Role
from app.api.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=BookPublication)
def create_book(
        book: BookPublication,
        current_user: Annotated[User, Depends(get_current_user)],
        session: Session = Depends(get_session)
):
    """
    Create a new Book.
    - Faculty can only create for themselves (faculty_id is ignored/overwritten).
    - Admins can create for others.
    """
    # Permission Logic
    if current_user.role == Role.FACULTY:
        # Force the book to belong to the logged-in user
        book.faculty_id = current_user.id

    # If Admin, we respect the 'faculty_id' sent in the JSON,
    # but we should check if that ID actually exists.
    elif current_user.role == Role.ADMIN:
        if not session.get(User, book.faculty_id):
            raise HTTPException(status_code=404, detail="Target faculty ID not found")

    session.add(book)
    session.commit()
    session.refresh(book)
    return book


@router.get("/", response_model=List[BookPublication])
def list_books(
        faculty_id: int | None = None,
        session: Session = Depends(get_session)
):
    """List all books, or filter by specific faculty_id."""
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

    # Only Admin or the Owner can delete
    if current_user.role != Role.ADMIN and book.faculty_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this book")

    session.delete(book)
    session.commit()
    return {"ok": True}