from flask import Flask, render_template, redirect, request, url_for, session
from models import db, Student, Class

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dashboard.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'supersecretkey'  # Required for session

db.init_app(app)

# Shared password to enter the app
ACCESS_PASSWORD = "secret123"

# ✅ Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ACCESS_PASSWORD:
            session['authenticated'] = True
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Incorrect password.")
    return render_template('login.html')

# ✅ Logout route
@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('login'))

# ✅ Protected route decorator
def login_required(view):
    def wrapper(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect(url_for('login'))
        return view(*args, **kwargs)
    wrapper.__name__ = view.__name__
    return wrapper

# ✅ New "/" route to start at login
@app.route('/')
def index():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

# ✅ Dashboard route (previously home)
@app.route('/dashboard')
@login_required
def dashboard():
    classes = Class.query.all()
    alice = Student.query.filter_by(name='Alice').first()  # Assuming 'Alice' is in the DB
    return render_template('home.html', classes=classes, alice=alice)

@app.route('/signup', methods=['POST'])
@login_required
def signup():
    student_id = int(request.form['student_id'])
    class_id = int(request.form['class_id'])
    student = Student.query.get(student_id)
    classroom = Class.query.get(class_id)

    if classroom not in student.classes:
        student.classes.append(classroom)
        db.session.commit()

    return redirect(url_for('student_classes', student_id=student.id))

@app.route('/unenroll/<int:student_id>/<int:class_id>', methods=['POST'])
@login_required
def unenroll(student_id, class_id):
    student = Student.query.get_or_404(student_id)
    classroom = Class.query.get_or_404(class_id)

    if classroom in student.classes:
        student.classes.remove(classroom)
        db.session.commit()

    return redirect(url_for('student_classes', student_id=student.id))

@app.route('/student/<int:student_id>')
@login_required
def student_classes(student_id):
    student = Student.query.get_or_404(student_id)
    return render_template('signup.html', student=student, classes=Class.query.all())

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

