from sqlmodel import Session, create_engine
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=False)

def get_session():
    """
    Dependency function.
    Opens a new DB session for a request, and closes it when the request is done.
    """
    with Session(engine) as session:
        yield session