from app import create_app, db
from app.models import Faculty, Paper

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """
    Creates a shell context that adds the database instance and models
    to the Flask shell session, making them accessible for testing and debugging.
    """
    return {'db': db, 'Faculty': Faculty, 'Paper': Paper}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
