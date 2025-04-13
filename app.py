
from flask import Flask, redirect, url_for, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from models import db, User, Course, Teacher, Student, Enrollment

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect('/adminpanel')
        return "Invalid credentials"
    return '''
    <head>
        <link rel="stylesheet" href="/static/adminstyle.css">
        <title>Admin Login</title>
    </head>
    <body>
        <div class="login-container">
            <h2>Admin Login</h2>
            <form method="POST" class="form-box">
                <label>Username:</label><br>
                <input name="username" type="text"><br>
                <label>Password:</label><br>
                <input name="password" type="password"><br>
                <input type="submit" value="Login">
            </form>
        </div>
    </body>'''

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return "Logged out"

@app.route('/adminpanel', methods=['GET', 'POST'])
@login_required
def admin_panel():
    courses = Course.query.all()
    teachers = Teacher.query.all()

    # Handle new course creation
    if request.method == 'POST':
        name = request.form.get('name')
        time = request.form.get('time')
        teacher_id = request.form.get('teacher_id')
        if name and time and teacher_id:
            new_course = Course(name=name, time=time, teacher_id=int(teacher_id))
            db.session.add(new_course)
            db.session.commit()
            return redirect('/adminpanel')
        
    if request.form.get('form_type') == 'add_teacher':
        teacher_name = request.form.get('teacher_name')
        if teacher_name:
            new_teacher = Teacher(name=teacher_name)
            db.session.add(new_teacher)
            db.session.commit()
            return redirect('/adminpanel')
        
    if request.form.get('form_type') == 'add_student':
        student_name = request.form.get('student_name')
        if student_name:
            new_student = Student(name=student_name)
            db.session.add(new_student)
            db.session.commit()
            return redirect('/adminpanel')

    html = '''
    <head>
        <link rel="stylesheet" href="/static/adminstyle.css">
    </head>
    <body>
    <h2>Courses</h2>
    <table border="1" cellpadding="5">
        <tr><th>Name</th><th>Teacher</th><th>Time</th><th>Students</th><th>Action</th></tr>'''
    for course in courses:
        html += f"<tr><td><a href='/course/{course.id}'>{course.name}</a></td><td>{course.teacher.name}</td><td>{course.time}</td><td>{len(course.enrollments)}</td>"
        html += f"<td><a href='/edit_course/{course.id}'>Edit</a></td></tr>"
    html += "</table><br>"

    # Add new course form
    html += '''
    <div style="display: flex; gap: 40px; margin-top: 20px;">

        <div style="display:inline-block; vertical-align:top;">
            <h3>Add New Course</h3>
            <form method="POST">
                <input type="hidden" name="form_type" value="add_course">
                <label>Course Name:</label><br>
                <input name="name"><br>
                <label>Time:</label><br>
                <input name="time"><br>
                <label>Teacher:</label><br>
                <select name="teacher_id">
                    <option value="">-- Select a teacher --</option>'''
    for t in teachers:
        html += f"<option value='{t.id}'>{t.name}</option>"
    html += '''</select><br><br>
            <input type="submit" value="Add Course">
        </form>
    </div>

    <div style="display:inline-block; vertical-align:top;">
        <h3>Add New Teacher</h3>
        <form method="POST">
            <input type="hidden" name="form_type" value="add_teacher">
            <label>Teacher Name:</label><br>
            <input name="teacher_name"><br><br>
            <input type="submit" value="Add Teacher">
        </form>
    </div>

    <div style="display:inline-block; vertical-align:top;">
        <h3>Add New Student</h3>
        <form method="POST">
            <input type="hidden" name="form_type" value="add_student">
            <label>Student Name:</label><br>
            <input name="student_name"><br><br>
            <input type="submit" value="Add Student">
        </form>
    </div>

    </div>
    '''
    html += '''
    <br><hr><h3>All Teachers</h3>
    <table border="1" cellpadding="5">
        <tr><th>ID</th><th>Name</th></tr>'''
    for teacher in teachers:
        html += f'''
        <tr>
            <td>{teacher.id}</td>
            <td>{teacher.name}</td>
            <td>
                <form method="POST" action="/delete_teacher/{teacher.id}" style="display:inline;">
                    <button type="submit" onclick="return confirm('Are you sure you want to delete this teacher?')">Delete</button>
                </form>
            </td>
        </tr>'''
    html += "</table>"

    students = Student.query.all()
    html += '''
    <br><h3>All Students</h3>
    <table border="1" cellpadding="5">
        <tr><th>ID</th><th>Name</th></tr>'''
    for student in students:
        html += f'''
        <tr>
            <td>{student.id}</td>
            <td>{student.name}</td>
            <td>
                <form method="POST" action="/delete_student/{student.id}" style="display:inline;">
                    <button type="submit" onclick="return confirm('Are you sure you want to delete this student?')">Delete</button>
                </form>
            </td>
        </tr>'''
    html += "</table>"

    html += "<br><a href='/logout'>Logout</a></body>"
    return html

@app.route('/edit_course/<int:course_id>', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    teachers = Teacher.query.all()

    if request.method == 'POST':
        course.name = request.form.get('name')
        course.time = request.form.get('time')
        course.teacher_id = int(request.form.get('teacher_id'))
        db.session.commit()
        return redirect('/adminpanel')

    html = f'''
    <head>
        <link rel="stylesheet" href="/static/adminstyle.css">
    </head>
    <body>
    <h2>Edit Course: {course.name}</h2>
    <form method="POST">
      <label>Name:</label><br>
      <input name="name" value="{course.name}"><br>
      <label>Time:</label><br>
      <input name="time" value="{course.time}"><br>
      <label>Teacher:</label><br>
      <select name="teacher_id">'''
    for t in teachers:
        selected = 'selected' if t.id == course.teacher_id else ''
        html += f'<option value="{t.id}" {selected}>{t.name}</option>'
    html += '''</select><br><br>
      <input type="submit" value="Save">
    </form>
    <br><a href="/adminpanel">Back to Admin Panel</a></body>'''
    return html

@app.route('/course/<int:course_id>', methods=['GET', 'POST'])
@login_required
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    all_students = Student.query.all()
    enrolled_ids = [e.student_id for e in course.enrollments]

    if request.method == 'POST':
        for enrollment in course.enrollments:
            grade_field = f"grade_{enrollment.student_id}"
            if grade_field in request.form:
                enrollment.grade = request.form[grade_field]

        new_student_id = request.form.get('new_student_id')
        if new_student_id and new_student_id != "":
            new_student_id = int(new_student_id)
            if new_student_id not in enrolled_ids:
                new_enrollment = Enrollment(student_id=new_student_id, course_id=course.id, grade='N/A')
                db.session.add(new_enrollment)

        if 'remove_student_id' in request.form:
            remove_id = int(request.form['remove_student_id'])
            Enrollment.query.filter_by(course_id=course.id, student_id=remove_id).delete()

        db.session.commit()
        return redirect(f'/course/{course.id}')

    html = f'''
    <head>
        <link rel="stylesheet" href="/static/adminstyle.css">
    </head>
    <body>
    <h2>Course: {course.name}</h2>
    <p>Teacher: {course.teacher.name} | Time: {course.time}</p>
    <form method='POST'><table border='1'><tr><th>Student</th><th>Grade</th><th>Remove</th></tr>'''
    for enrollment in course.enrollments:
        html += f"<tr><td>{enrollment.student.name}</td>"
        html += f"<td><input name='grade_{enrollment.student.id}' value='{enrollment.grade}'></td>"
        html += f"<td><button name='remove_student_id' value='{enrollment.student.id}'>Remove</button></td></tr>"
    html += '''</table><br>

    <label>Add Student:</label><select name='new_student_id'>"
    "<option value=''>-- Select a student --</option>'''
    for student in all_students:
        if student.id not in enrolled_ids:
            html += f"<option value='{student.id}'>{student.name}</option>"
    html += '''</select><br><br><input type='submit' value='Save Changes'></form>
    <br><a href='/adminpanel'>Back to Admin Panel</a></body>'''
    return html

@app.route('/delete_teacher/<int:teacher_id>', methods=['POST'])
@login_required
def delete_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    db.session.delete(teacher)
    db.session.commit()
    return redirect('/adminpanel')

@app.route('/delete_student/<int:student_id>', methods=['POST'])
@login_required
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    return redirect('/adminpanel')

if __name__ == '__main__':
    app.run(debug=True)
