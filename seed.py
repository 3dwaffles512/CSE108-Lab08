from app import app, db
from models import Student, Class

with app.app_context():
    db.drop_all()      # Drops all tables
    db.create_all()    # Recreates the tables
    s1 = Student(name='Alice')
    c1 = Class(title='Math 101')
    c2 = Class(title='History 202')
    db.session.add_all([s1, c1, c2])
    db.session.commit()
    
    print(f"Alice created with ID: {s1.id}")
