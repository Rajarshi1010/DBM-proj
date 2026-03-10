from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.base import get_session
from app.models.conference import ConferencePublication, ConferenceCreate, ConferenceRead, ConferenceUpdate
from app.models.user import User, Role
from app.api.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=ConferenceRead)
def create_conference(
    conf_in: ConferenceCreate, # <--- CHANGED
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session)
):
    data = conf_in.model_dump(exclude={"faculty_id"})
    conf_db = ConferencePublication(**data)

    if current_user.role == Role.FACULTY:
        conf_db.faculty_id = current_user.id
    elif current_user.role == Role.ADMIN:
        if not conf_in.faculty_id:
            raise HTTPException(status_code=400, detail="Admins must provide 'faculty_id'.")
        if not session.get(User, conf_in.faculty_id):
            raise HTTPException(status_code=404, detail="Target faculty not found")
        conf_db.faculty_id = conf_in.faculty_id

    session.add(conf_db)
    session.commit()
    session.refresh(conf_db)
    return conf_db


@router.patch("/{conference_id}", response_model=ConferenceRead)
def update_conference(
    conference_id: int,
    conference_in: ConferenceUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Session = Depends(get_session)
):
    # 1. Fetch the existing record
    db_conf = session.get(ConferencePublication, conference_id)
    if not db_conf:
        raise HTTPException(status_code=404, detail="Conference entry not found")

    # 2. Authorization: Admins can edit anything; Faculty only their own
    if current_user.role != Role.ADMIN and db_conf.faculty_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this entry")

    # 3. Extract data (exclude_unset=True ensures we only update what was sent)
    update_data = conference_in.model_dump(exclude_unset=True)

    # 4. Handle Admin-only ownership changes
    if "faculty_id" in update_data:
        if current_user.role == Role.ADMIN:
            if not session.get(User, update_data["faculty_id"]):
                raise HTTPException(status_code=404, detail="Target faculty not found")
        else:
            del update_data["faculty_id"]

    # 5. Apply changes
    for key, value in update_data.items():
        setattr(db_conf, key, value)

    session.add(db_conf)
    session.commit()
    session.refresh(db_conf)
    return db_conf

@router.get("/", response_model=List[ConferenceRead])
def list_conferences(faculty_id: int | None = None, session: Session = Depends(get_session)):
    query = select(ConferencePublication)
    if faculty_id: query = query.where(ConferencePublication.faculty_id == faculty_id)
    return session.exec(query).all()


@router.delete("/{conf_id}")
def delete_conference(
        conf_id: int,
        current_user: Annotated[User, Depends(get_current_user)],
        session: Session = Depends(get_session)
):
    conference = session.get(ConferencePublication, conf_id)
    if not conference:
        raise HTTPException(status_code=404, detail="Conference paper not found")
    if current_user.role != Role.ADMIN and conference.faculty_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this entry")

    session.delete(conference)
    session.commit()
    return {"ok": True}