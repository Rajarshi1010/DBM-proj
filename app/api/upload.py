from typing import Any
from fastapi import APIRouter, UploadFile, File, Depends
from sqlmodel import Session, select
import pandas as pd
import io
import re
from app.db.base import get_session
from app.models.user import User, Role
from app.models.book import BookPublication
from app.models.conference import ConferencePublication
from app.models.journal import JournalPublication
from app.api.auth import get_current_user

router = APIRouter()


def normalize_string(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = re.sub(r'^(dr\.|prof\.|mr\.|ms\.)\s*', '', text.lower().strip())
    return re.sub(r'[^a-z0-9]', '', text)


HEADER_MAP = {
    "title": "title",
    "titleofbook": "title",
    "booktitle": "title",

    "titleofpaper": "title_of_paper",
    "papertitle": "title_of_paper",

    "year": "publication_month_year",
    "publicationyear": "publication_month_year",
    "monthandyear": "publication_month_year",
    "monthyear": "publication_month_year",
    "publicationmonthyear": "publication_month_year",

    # Book Fields
    "publisher": "publisher_details",
    "publisherdetails": "publisher_details",

    # Conference Fields
    "conferencename": "conference_name",
    "heldon": "held_on",
    "date": "held_on",
    "place": "place",
    "location": "place",
    "isbn": "isbn",
    "isbnno": "isbn",

    # Journal Fields
    "journalname": "journal_name",
    "type": "journal_type",
    "journaltype": "journal_type",

    "urldoi": "url_doi",
    "doi": "url_doi",

    "issn": "issn",
    "issnno": "issn",

    "pagenumbers": "page_numbers",
    "pages": "page_numbers",

    # Name Identifiers
    "facultyname": "faculty_name",
    "author": "faculty_name",
    "authorname": "faculty_name",
    "faculty": "faculty_name",

    # Email Identifiers
    "email": "email",
    "emailid": "email",
    "facultyemail": "email",
    "authoremail": "email"
}


def clean_headers(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [normalize_string(col) for col in df.columns]
    rename_dict = {}
    for col in df.columns:
        if col in HEADER_MAP:
            rename_dict[col] = HEADER_MAP[col]
    return df.rename(columns=rename_dict)


def process_upload(
        df: pd.DataFrame,
        model_class: Any,
        session: Session,
        current_user: User
) -> dict:
    # Fetch all users
    users = session.exec(select(User)).all()

    # Map users strictly by email for collision-proof lookups
    user_map = {u.email.lower().strip(): u.id for u in users if u.email}

    success_count = 0
    errors = []

    for index, row in df.iterrows():
        try:
            row_data = row.to_dict()

            # Extract both Name (for logs) and Email (for mapping)
            author_name = row_data.get("faculty_name", "Unknown Faculty")
            author_email = row_data.get("email")

            # 1. Check if Email is missing
            if not author_email or pd.isna(author_email):
                errors.append(f"Row {index + 2}: Missing Email for '{author_name}'. Cannot map to database.")
                continue

            # Clean the email
            cleaned_email = str(author_email).lower().strip()

            # 2. Lookup the ID using the email
            faculty_id = user_map.get(cleaned_email)

            if not faculty_id:
                errors.append(f"Row {index + 2}: Faculty '{author_name}' with email '{author_email}' not found.")
                continue

            # 3. Permission Check
            if current_user.role != Role.ADMIN and faculty_id != current_user.id:
                errors.append(f"Row {index + 2}: Permission Denied. You cannot upload for '{author_name}'.")
                continue

            # 4. Clean Data & Handle Title Mismatches
            clean_data = {}
            for k, v in row_data.items():
                # Fix: Header mismatches
                if k == "title" and "title_of_paper" in model_class.model_fields:
                    k = "title_of_paper"
                elif k == "title_of_paper" and "title" in model_class.model_fields:
                    k = "title"

                # Check if value is not empty
                if k in model_class.model_fields and pd.notna(v) and str(v).strip() != "":
                    val = v

                    # ---> NEW: Clean the actual data value! <---
                    if isinstance(val, str):
                        # Remove invisible spaces, line breaks, and Excel artifacts (\xa0)
                        val = val.strip().replace('\xa0', '')

                        # If it's an Enum like journal_type, force it to match your strict DB format
                        if k == "journal_type":
                            val = val.upper()

                    clean_data[k] = val

            # 5. Create Object and inject the bulletproof faculty_id
            db_obj = model_class(**clean_data)
            db_obj.faculty_id = faculty_id

            session.add(db_obj)
            session.commit()
            success_count += 1

        except Exception as e:
            session.rollback()
            errors.append(f"Row {index + 2}: Error processing - {str(e)}")

    return {
        "status": "completed",
        "added": success_count,
        "failed": len(errors),
        "errors": errors
    }


@router.post("/books")
async def upload_books(
        file: UploadFile = File(...),
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    contents = await file.read()
    df = pd.read_excel(io.BytesIO(contents))
    df = clean_headers(df)
    return process_upload(df, BookPublication, session, current_user)


@router.post("/conferences")
async def upload_conferences(
        file: UploadFile = File(...),
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    contents = await file.read()
    df = pd.read_excel(io.BytesIO(contents))
    df = clean_headers(df)
    return process_upload(df, ConferencePublication, session, current_user)


@router.post("/journals")
async def upload_journals(
        file: UploadFile = File(...),
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    contents = await file.read()
    df = pd.read_excel(io.BytesIO(contents))
    df = clean_headers(df)
    return process_upload(df, JournalPublication, session, current_user)