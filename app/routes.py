from flask import Blueprint, request, jsonify
from .models import db, Paper, Faculty
import pandas as pd
from datetime import datetime

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/papers', methods=['GET'])
def get_papers():
    query = Paper.query

    faculty_name = request.args.get('faculty_name')
    title = request.args.get('title')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if faculty_name:
        query = query.join(Paper.authors).filter(Faculty.faculty_name.ilike(f'%{faculty_name}%'))
    if title:
        query = query.filter(Paper.title.ilike(f'%{title}%'))
    if start_date:
        query = query.filter(Paper.publishing_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(Paper.publishing_date <= datetime.strptime(end_date, '%Y-%m-%d').date())

    papers = query.all()
    # The response now provides the faculty 'id' instead of 'serial_no'.
    return jsonify([{
        'title': paper.title,
        'publishing_date': paper.publishing_date.isoformat(),
        'volume_no': paper.volume_no,
        'authors': [{'name': author.faculty_name, 'id': author.id} for author in paper.authors]
    } for paper in papers])

@bp.route('/upload', methods=['POST'])
def upload_papers():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file provided'}), 400

    try:
        df = pd.read_excel(file)
        for _, row in df.iterrows():
            with db.session.begin_nested():
                paper = Paper(
                    title=row['title'],
                    publishing_date=pd.to_datetime(row['publishing_date']).date(),
                    volume_no=row['volume_no']
                )
                db.session.add(paper)

                # Expects 'author_ids' column in Excel; finds Faculty by the new string ID.
                author_ids = [s.strip() for s in str(row['author_ids']).split(';')]
                for faculty_id in author_ids:
                    faculty = Faculty.query.filter_by(id=faculty_id).first()
                    if faculty:
                        paper.authors.append(faculty)
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Upload successful'})
