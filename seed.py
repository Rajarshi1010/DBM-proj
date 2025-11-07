from app import create_app, db
from app.models import Faculty, Paper
from datetime import date

app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()

    # --- Create Sample Faculty with alphanumeric IDs ---
    faculty1 = Faculty(id='F101', faculty_name='Dr. Alice Smith')
    faculty2 = Faculty(id='F102', faculty_name='Dr. Bob Johnson')
    faculty3 = Faculty(id='F103', faculty_name='Dr. Carol White')
    db.session.add_all([faculty1, faculty2, faculty3])
    db.session.commit()

    # --- Create Sample Papers (no changes needed here) ---
    paper1 = Paper(
        title='The Theory of Everything',
        publishing_date=date(2023, 5, 15),
        volume_no='Vol. 1'
    )
    paper1.authors.extend([faculty1, faculty2])

    paper2 = Paper(
        title='Advanced Quantum Mechanics',
        publishing_date=date(2023, 8, 20),
        volume_no='Vol. 2'
    )
    paper2.authors.append(faculty2)

    paper3 = Paper(
        title='A Study of Neural Networks',
        publishing_date=date(2024, 1, 10),
        volume_no='Vol. 3'
    )
    paper3.authors.extend([faculty1, faculty3])

    db.session.add_all([paper1, paper2, paper3])
    db.session.commit()

    print("Database seeded with updated schema and sample data.")
