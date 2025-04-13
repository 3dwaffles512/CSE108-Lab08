from app import app
from models import db, User, Teacher, Course, Student, Enrollment

with app.app_context():
    db.drop_all()
    db.create_all()

    # Admin user
    admin = User(username='admin', password='pass')
    db.session.add(admin)

    # Teachers
    t1 = Teacher(name='Dr. Smith')
    t2 = Teacher(name='Prof. Johnson')
    t3 = Teacher(name='Dr. Adams')
    t4 = Teacher(name='Prof. Baker')
    t5 = Teacher(name='Dr. Clark')
    t6 = Teacher(name='Prof. Davis')
    t7 = Teacher(name='Dr. Evans')
    db.session.add_all([t1, t2, t3, t4, t5, t6, t7])
    db.session.commit()

    # Courses
    c1 = Course(name='Math 101', time='MWF 9AM', teacher_id=t1.id)
    c2 = Course(name='History 201', time='TTh 11AM', teacher_id=t2.id)
    c3 = Course(name='Physics 150', time='MWF 2PM', teacher_id=t3.id)
    c4 = Course(name='Biology 110', time='TTh 9AM', teacher_id=t4.id)
    c5 = Course(name='Computer Science 101', time='MWF 11AM', teacher_id=t5.id)
    c6 = Course(name='Philosophy 210', time='TTh 2PM', teacher_id=t6.id)
    c7 = Course(name='Economics 220', time='MWF 3PM', teacher_id=t7.id)
    db.session.add_all([c1, c2, c3, c4, c5, c6, c7])
    db.session.commit()

    # Students
    s1 = Student(name='Alice')
    s2 = Student(name='Bob')
    s3 = Student(name='Charlie')
    s4 = Student(name='Diana')
    s5 = Student(name='Ethan')
    s6 = Student(name='Fiona')
    s7 = Student(name='George')
    s8 = Student(name='Hannah')
    db.session.add_all([s1, s2, s3, s4, s5, s6, s7, s8])
    db.session.commit()

    # Enrollments
    enrollments = [
        Enrollment(student_id=s1.id, course_id=c1.id, grade='A'),
        Enrollment(student_id=s2.id, course_id=c1.id, grade='B'),
        Enrollment(student_id=s3.id, course_id=c2.id, grade='A-'),
        Enrollment(student_id=s4.id, course_id=c3.id, grade='B+'),
        Enrollment(student_id=s5.id, course_id=c4.id, grade='A'),
        Enrollment(student_id=s6.id, course_id=c5.id, grade='B'),
        Enrollment(student_id=s7.id, course_id=c6.id, grade='A-'),
        Enrollment(student_id=s8.id, course_id=c7.id, grade='A'),
    ]
    db.session.add_all(enrollments)
    db.session.commit()

    print("Sample data with extra teachers, courses, and students created.")
