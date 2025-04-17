from flask import Flask, render_template, redirect, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dashboard.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'supersecretkey'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)
    role = db.Column(db.String(10), nullable=False)

class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))
    grade = db.Column(db.String(5))

    student = db.relationship('Student', backref='enrollments')
    course = db.relationship('Class', backref='enrollments')

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    classes = db.relationship('Class', secondary='enrollments', backref='students')

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(100))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    teacher = db.relationship('Teacher', backref='classes')
    capacity = db.Column(db.Integer, default=30)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('admin_panel'))
            elif user.role == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            elif user.role == 'student':
                student = Student.query.filter_by(user_id=user.id).first()
                if student:
                    return redirect(url_for('student_dashboard', student_id=student.id))
                else:
                    return "Student profile not found", 404
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ---------- Admin ----------
@app.route('/adminpanel', methods=['GET', 'POST'])
@login_required
def admin_panel():
       
         
    # Handle new course creation
       courses = Class.query.all()
       teachers = Teacher.query.all()
       students = Student.query.all()

       if request.method == 'POST':
        title = request.form.get('name')
        time = request.form.get('time')
        capacity = request.form.get('capacity', 30)
        teacher_id = request.form.get('teacher_id')
        if title and time and teacher_id:
            new_course = Class(title=title, time=time, teacher_id=int(teacher_id), capacity=int(capacity))
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

    # This return is now outside the POST block
       return render_template('admin_panel.html', courses=courses, teachers=teachers, students=students)


@app.route('/edit_course/<int:course_id>', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    course = Class.query.get_or_404(course_id)
    teachers = Teacher.query.all()
    all_students = Student.query.all()
    enrolled_ids = [e.student_id for e in course.enrollments]

    error = None

    if request.method == 'POST':
        course.name = request.form.get('title')
        course.time = request.form.get('time')
        course.capacity = int(request.form.get('capacity', course.capacity))
        course.teacher_id = int(request.form.get('teacher_id'))

        for enrollment in course.enrollments:
            grade_field = f"grade_{enrollment.student_id}"
            if grade_field in request.form:
                enrollment.grade = request.form[grade_field]

        new_student_id = request.form.get('new_student_id')
        if new_student_id:
            new_student_id = int(new_student_id)
            if new_student_id not in enrolled_ids:
                if len(course.students) >= course.capacity:
                    error = f"Class is full. Max capacity is {course.capacity}."
                else:
                    db.session.add(Enrollment(student_id=new_student_id, class_id=course.id, grade='N/A'))

        if 'remove_student_id' in request.form:
            remove_id = int(request.form['remove_student_id'])
            Enrollment.query.filter_by(class_id=course.id, student_id=remove_id).delete()

        if not error:
            db.session.commit()
            return redirect('/adminpanel')

    return render_template('edit_course.html', course=course, teachers=teachers, all_students=all_students, enrolled_ids=enrolled_ids, error=error)

@app.route('/course/<int:course_id>', methods=['GET', 'POST'])
@login_required
def course_detail(course_id):
    course = Class.query.get_or_404(course_id)
    all_students = Student.query.all()
    enrolled_ids = [e.student_id for e in course.enrollments]

    if request.method == 'POST':

        course.title = request.form.get('title', course.title)
        course.time = request.form.get('time', course.time)
        course.capacity = int(request.form.get('capacity', course.capacity))

        for enrollment in course.enrollments:
            grade_field = f"grade_{enrollment.student_id}"
            if grade_field in request.form:
                enrollment.grade = request.form[grade_field]

        new_student_id = request.form.get('new_student_id')
        if new_student_id:
            new_student_id = int(new_student_id)
            if new_student_id not in enrolled_ids:
                new_enrollment = Enrollment(student_id=new_student_id, course_id=course.id, grade='N/A')
                db.session.add(new_enrollment)

        if 'remove_student_id' in request.form:
            remove_id = int(request.form['remove_student_id'])
            Enrollment.query.filter_by(course_id=course.id, student_id=remove_id).delete()

        db.session.commit()
        return redirect(url_for('course_detail', course_id=course.id))

    return render_template('course_detail.html', course=course, all_students=all_students, enrolled_ids=enrolled_ids)

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
     

# ---------- Student ----------
@app.route('/student/<int:student_id>')
@login_required
def student_dashboard(student_id):
    student = Student.query.get_or_404(student_id)
    classes = Class.query.all()
    enrollments = Enrollment.query.filter_by(student_id=student.id).all()
    return render_template('signup.html', student=student, classes=classes, enrollments=enrollments)

@app.route('/signup', methods=['POST'])
@login_required
def signup():
    student_id = int(request.form['student_id'])
    class_id = int(request.form['class_id'])
    student = Student.query.get(student_id)
    classroom = Class.query.get(class_id)

    if len(classroom.students) >= classroom.capacity:
        return f"This class is full. Max capacity is {classroom.capacity}.", 400
    if classroom not in student.classes:
        student.classes.append(classroom)
        db.session.commit()
    return redirect(url_for('student_dashboard', student_id=student.id))

@app.route('/unenroll/<int:student_id>/<int:class_id>', methods=['POST'])
@login_required
def unenroll(student_id, class_id):
    student = Student.query.get_or_404(student_id)
    classroom = Class.query.get_or_404(class_id)
    if classroom in student.classes:
        student.classes.remove(classroom)
        db.session.commit()
    return redirect(url_for('student_dashboard', student_id=student.id))

# ---------- Teacher ----------
@app.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        return redirect(url_for('login'))
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    classes = Class.query.filter_by(teacher_id=teacher.id).all()
    return render_template('teacher_dashboard.html', teacher=teacher, classes=classes)

@app.route('/teacher/course/<int:class_id>', methods=['GET', 'POST'])
@login_required
def teacher_class_detail(class_id):
    course = Class.query.get_or_404(class_id)
    enrollments = Enrollment.query.filter_by(class_id=class_id).all()
    if request.method == 'POST':
        for enrollment in enrollments:
            grade_field = f"grade_{enrollment.student_id}"
            if grade_field in request.form:
                enrollment.grade = request.form[grade_field]
        db.session.commit()
        return redirect(url_for('teacher_class_detail', class_id=class_id))
    return render_template('teacher_course_detail.html', course=course, enrollments=enrollments)
@app.route('/debug/users')
def debug_users():
    users = User.query.all()
    return '<br>'.join(f"Username: {u.username}, Password: {u.password}, Role: {u.role}" for u in users)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
