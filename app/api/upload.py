from typing import  Any
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
    # Remove 'Dr.', 'Prof.', 'Mr.', 'Ms.' (case insensitive)
    text = re.sub(r'^(dr\.|prof\.|mr\.|ms\.)\s*', '', text.lower().strip())
    return re.sub(r'[^a-z0-9]', '', text)

HEADER_MAP = {
    # Common Fields
    "title": "title",
    "titleofbook": "title",
    "booktitle": "title",
    "titleofpaper": "title_of_paper",
    "papertitle": "title_of_paper",
    "year": "publication_month_year",
    "publicationyear": "publication_month_year",
    "monthandyear": "publication_month_year",
    "month&year": "publication_month_year",

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

    # Faculty Identifier Fields
    "facultyname": "faculty_name",
    "author": "faculty_name",
    "authorname": "faculty_name",
    "faculty": "faculty_name"
}


def clean_headers(df: pd.DataFrame) -> pd.DataFrame:
    #Renames dataframe columns based on the map
    df.columns = [normalize_string(col) for col in df.columns]  # normalize excel headers

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
    users = session.exec(select(User)).all()
    user_map = {normalize_string(u.name): u.id for u in users}

    success_count = 0
    errors = []

    # Iterate Rows
    for index, row in df.iterrows():
        try:
            row_data = row.to_dict()
            # 1. Map Faculty Name to ID
            author_name = row_data.get("faculty_name")
            if not author_name or pd.isna(author_name):
                errors.append(f"Row {index + 2}: Missing Faculty Name")
                continue
            normalized_author = normalize_string(str(author_name))
            faculty_id = user_map.get(normalized_author)

            if not faculty_id:
                errors.append(f"Row {index + 2}: Faculty '{author_name}' not found.")
                continue
            # Permission Check
            if current_user.role != Role.ADMIN and faculty_id != current_user.id:
                errors.append(f"Row {index + 2}: Permission Denied. You cannot upload for '{author_name}'.")
                continue

            # 2. Clean Data: Remove empty or NaN fields
            clean_data = {}
            for k, v in row_data.items():
                if k in model_class.model_fields and pd.notna(v) and str(v).strip() != "":
                    clean_data[k] = v
            # 3. Create Object (issn or similar fields to be set as none if missing)
            db_obj = model_class(**clean_data)
            db_obj.faculty_id = faculty_id

            session.add(db_obj)
            success_count += 1

        except Exception as e:
            errors.append(f"Row {index + 2}: Error processing - {str(e)}")

    session.commit()

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