from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Date, Table, ForeignKey
from sqlalchemy.orm import relationship

db = SQLAlchemy()

# Association table for the many-to-many relationship between Paper and Faculty.
# The 'faculty_id' is now a String to match the Faculty's new primary key.
paper_authors = Table('paper_authors', db.metadata,
    Column('paper_id', Integer, ForeignKey('paper.id'), primary_key=True),
    Column('faculty_id', String(20), ForeignKey('faculty.id'), primary_key=True)
)

class Faculty(db.Model):
    """
    Represents a faculty member in the database.
    The 'id' is now an alphanumeric string and the primary key.
    """
    id = Column(String(20), primary_key=True)
    faculty_name = Column(String, nullable=False, index=True)

    papers = relationship('Paper', secondary=paper_authors, back_populates='authors')

class Paper(db.Model):
    """
    Represents a research paper in the database.
    """
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False, index=True)
    publishing_date = Column(Date, nullable=False, index=True)
    volume_no = Column(String)

    authors = relationship('Faculty', secondary=paper_authors, back_populates='papers')
