from app import app, db, User, Teacher, Student, Class, Enrollment

with app.app_context():
    db.drop_all()
    db.create_all()

    # Users
    admin = User(username="admin", password="admin", role="admin")
    teacher_user2 = User(username="teach2", password="teach2", role="teacher")
    teacher_user3 = User(username="teach3", password="teach3", role="teacher")
    student_user1 = User(username="student1", password="student1", role="student")

    db.session.add_all([admin, teacher_user2, teacher_user3, student_user1])
    db.session.commit()

    # Teachers
    teacher2 = Teacher(name="Susan Walker", user_id=teacher_user2.id)
    teacher3 = Teacher(name="Ammon Hepworth", user_id=teacher_user3.id)

    db.session.add_all([teacher2, teacher3])
    db.session.commit()

    # Student
    student1 = Student(name="Jose Santos", user_id=student_user1.id)
    db.session.add(student1)
    db.session.commit()

    # Classes
    class2 = Class(title="Physics 121", time="TR 11:00AM", teacher_id=teacher2.id)
    class3 = Class(title="CS 106", time="MWF 2:00PM", teacher_id=teacher3.id)
    db.session.add_all([class2, class3])
    db.session.commit()

    # Enroll student in a class with grades
    enrollment = Enrollment(student_id=student1.id, class_id=class2.id, grade="A")
    db.session.add(enrollment)
    db.session.commit()

    print("Database seeded successfully with users, teachers, student, classes, and enrollment.")
