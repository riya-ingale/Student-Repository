# THIS ISN'T COMPLETE

from flask import Flask, render_template, url_for, request, redirect, session, flash, send_file
from flask import make_response, session, g
import pdfkit
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from io import BytesIO
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import os
# from flask_admin import Admin
# from flask_admin.contrib.sqla import ModelView
import smtplib


app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "You need to Login first"


@login_manager.user_loader
def load_user(user_id):
    return Student.query.get(int(user_id))


# Mentors can have many students but a student can have just one mentor.
# Therefore we use One-Many Relationship in SqlaAlchemy

class Student(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(15))
    mname = db.Column(db.String(15))
    sname = db.Column(db.String(15))
    rollno = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(80))
    dob = db.Column(db.String(15))
    age = db.Column(db.String(23))
    gender = db.Column(db.String(15))
    mobno = db.Column(db.String(15))
    email = db.Column(db.String(50))
    yog = db.Column(db.String(15))

    dept = db.Column(db.String(15))
    div = db.Column(db.String(15))
    batchno = db.Column(db.String(1))

    cllg = db.Column(db.String(80))
    cllgboard = db.Column(db.String(80))
    marks12 = db.Column(db.String(80))
    compyear12 = db.Column(db.String(80))
    school = db.Column(db.String(80))
    schoolboard = db.Column(db.String(80))
    marks10 = db.Column(db.String(80))
    compyear10 = db.Column(db.String(80))
    cgpa = db.Column(db.String(80))

    marksheet12name = db.Column(db.String(100))
    marksheet12 = db.Column(db.LargeBinary)
    marksheet12verify = db.Column(db.String(20))

    marksheet10name = db.Column(db.String(100))
    marksheet10 = db.Column(db.LargeBinary)
    marksheet10verify = db.Column(db.String(20))

    marksheetlastsemname = db.Column(db.String(100))
    marksheetlastsem = db.Column(db.LargeBinary)
    marksheetlastsemverify = db.Column(db.String(20))

    certificate1name = db.Column(db.String(100))
    certificate1 = db.Column(db.LargeBinary)
    certificate1verify = db.Column(db.String(20))

    certificate2name = db.Column(db.String(100))
    certificate2 = db.Column(db.LargeBinary)
    certificate2verify = db.Column(db.String(20))

    certificate3name = db.Column(db.String(100))
    certificate3 = db.Column(db.LargeBinary)
    certificate3verify = db.Column(db.String(20))

    certificate4name = db.Column(db.String(100))
    certificate4 = db.Column(db.LargeBinary)
    certificate4verify = db.Column(db.String(20))

    certificate5name = db.Column(db.String(100))
    certificate5 = db.Column(db.LargeBinary)
    certificate5verify = db.Column(db.String(20))

    image_file = db.Column(db.String(20), nullable=False,
                           default="default.jpg")

    mentor_id = db.Column(db.Integer, db.ForeignKey(
        'mentor.id'))  # actual column

    def __repr__(self):
        return '<Student %r>' % (self.fname)


class Mentor(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(20))
    # do the Student table gets a pseudo column called mentor
    students = db.relationship('Student', backref='mentor')

    def __repr__(self):
        return '<Mentor %r>' % (self.username)

# admin = Admin(app)

# admin.add_view(ModelView(Student, db.session))
# admin.add_view(ModelView(Mentor, db.session))


@app.route('/')
def index():
    return render_template("index2.html")


@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == "POST":
        rollno = request.form['rollno']
        password = request.form['password']

        user = Student.query.filter_by(rollno=rollno).first()

        if not user:
            flash("No such Student found, Try Signing Up First", "warning")
            return redirect("/signUp")

        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for("feed", currentuser=current_user))
            else:
                flash("Incorrect password", "danger")
                return redirect("login")

    return render_template("login.html")


@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        user = Mentor.query.filter_by(username=session['user']).first()
        g.user = user


@app.route('/mentorLogin', methods=['GET', 'POST'])
def mentorLogin():
    if request.method == "POST":
        # print("POST request made")
        session.pop('user', None)
        # print("session popped")
        username = request.form['username']
        password = request.form['password']
        # print("Got the username and password")
        mentor = Mentor.query.filter_by(username=username).first()
        if mentor:
            if mentor.password == password:
                # print("password is correct")
                session['user'] = username
                # print("session set")
                return redirect(url_for('mentor'))
            else:
                flash("Incorrect Password")
                # print("Password incorrect")
        else:
            flash("No such Mentor is Registered")
            # print("admin doesnt exist")
    return render_template("mentorLogin.html")


@app.route('/signUp', methods=['GET', 'POST'])
def signUp():
    if request.method == "POST":
        fname = request.form['fname']
        rollno = request.form['rollno']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method="sha256")
        cpassword = request.form['cpassword']
        email = request.form['email']
        mobno = request.form['mobno']
        mentorname = request.form['mentor']
        mentor = Mentor.query.filter_by(username=mentorname).first()
        user = Student.query.filter_by(rollno=rollno).first()
        if user:
            flash("User with the Roll No. Already Exists", "warning")
            return redirect("/signUp")
        if(password == cpassword):
            new_user = Student(fname=fname, rollno=rollno, password=hashed_password,
                               email=email, mobno=mobno, mentor=mentor)
            db.session.add(new_user)
            message = "You have been succesfully registered in the Student Repository!\nThank You For Registering."
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login("studentrepository20@gmail.com", "studentrepo")
            server.sendmail("studentrepository20@gmail.com", email, message)
            db.session.commit()
            flash("Sucessfully Registered!", "success")
            return redirect('/login')
        else:
            flash("Passwords don't match", "danger")
            return redirect("/signUp")

    return render_template("signUp.html")


@app.route('/logout', methods=["POST", "GET"])
def logout():
    logout_user()
    flash("Sucessfully Logged Out")
    return redirect('/login')


@app.route('/dropsession', methods=['POST', "GET"])
def dropsession():
    session.pop('user', None)
    flash("Sucessfully Logged Out")
    return render_template('mentorLogin.html')


@app.route('/mentor', methods=['POST', 'GET'])
def mentor():
    if g.user:
        return render_template("mentor.html", user=session['user'])
    flash("You need to Login First")
    return redirect(url_for('mentorLogin'))


# Logic for saving the user's uploaded pictures into our file system
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    print(f_ext)
    picture_path = os.path.join(
        app.root_path, 'static\profile_pics', picture_fn)
    print(picture_path)
    form_picture.save(picture_path)
    print("form_picture Saved")
    return picture_fn


@app.route('/profilepic/<int:student_id>', methods=['POST'])
def profilepic(student_id):
    print("inside profile pic function")
    student = Student.query.filter_by(id=student_id).first()
    print("Query for one student")
    picture_file = save_picture(request.files['profile_pic'])
    print("picture_file variable assigned")
    print(picture_file)
    student.image_file = picture_file
    db.session.commit()
    print("Session commited")
    return redirect(url_for("feed", currentuser=current_user))


@app.route('/deletepic/<int:student_id>', methods=['POST'])
def deletepic(student_id):
    if request.method == 'POST':
        student = Student.query.filter_by(id=student_id).first()
        student.image_file = "default.jpg"
        db.session.commit()
        return redirect(url_for("feed", currentuser=current_user))


@app.route('/feed', methods=['POST', 'GET'])
@login_required
def feed():
    return render_template("Feed.html", currentuser=current_user)


@app.route('/addgen/<int:student_id>', methods=['POST'])
def addgen(student_id):
    if request.method == 'POST':
        student = Student.query.filter_by(id=student_id).first()
        student.fname = request.form.get("fname")
        student.mname = request.form.get("mname")
        student.sname = request.form.get("sname")
        student.rollno = request.form.get("rollno")
        student.dob = request.form.get("dob")
        student.age = request.form.get("age")
        student.gender = request.form.get("gender")
        student.mobno = request.form.get("mobno")
        student.email = request.form.get("email")
        student.dept = request.form.get("dept")
        student.div = request.form.get("div")
        student.yog = request.form.get("yog")
        student.batchno = request.form.get("batchno")
        db.session.commit()
        return redirect(url_for("feed", currentuser=current_user))


@app.route('/addedu/<int:student_id>', methods=['POST'])
def addedu(student_id):
    if request.method == 'POST':
        student = Student.query.filter_by(id=student_id).first()

        student.cllg = request.form.get("cllg")
        student.cllgboard = request.form.get("cllgboard")
        student.marks12 = request.form.get("marks12")
        student.compyear12 = request.form.get("compyear12")

        student.school = request.form.get("school")
        student.schoolboard = request.form.get("schoolboard")
        student.marks10 = request.form.get("marks10")
        student.compyear10 = request.form.get("compyear10")
        db.session.commit()
        return redirect(url_for("feed", currentuser=current_user))


# Uploading the Documents
@app.route('/uploadmarksheet12/<int:student_id>', methods=["POST"])
@login_required
def uploadmarksheet12(student_id):
    file = request.files['marksheet12']
    if len(file.filename) > 0:
        student = Student.query.filter_by(id=student_id).first()
        student.marksheet12name = file.filename
        student.marksheet12 = file.read()
        db.session.commit()
        flash("File Successfully added", "success")
        return redirect(url_for("feed", currentuser=current_user))
    else:
        flash("Select a file first", "warning")
        return redirect(url_for("feed", currentuser=current_user))


@app.route('/uploadmarksheet10/<int:student_id>', methods=["GET", "POST"])
@login_required
def uploadmarksheet10(student_id):
    file = request.files['marksheet10']
    print("got the file")
    student = Student.query.filter_by(id=student_id).first()
    print("got the row")
    student.marksheet10name = file.filename
    student.marksheet10 = file.read()
    print("added but not commimted")
    db.session.commit()
    print("added the marksheet")
    return redirect(url_for("feed", currentuser=current_user))


@app.route('/uploadmarksheetlastsem/<int:student_id>', methods=["GET", "POST"])
@login_required
def uploadmarksheetlastsem(student_id):
    file = request.files['marksheetlastsem']
    print("got the file")
    student = Student.query.filter_by(id=student_id).first()
    print("got the row")
    student.marksheetlastsemname = file.filename
    student.marksheetlastsem = file.read()
    print("added but not commimted")
    db.session.commit()
    print("added the marksheet")
    return redirect(url_for("feed", currentuser=current_user))


# Downloading the Documents

@app.route('/downloadmarksheet12/<int:student_id>', methods=['GET', 'POST'])
def downloadmarksheet12(student_id):
    student = Student.query.filter_by(id=student_id).first()
    if len(student.marksheet12name) > 1:
        file_data = student.marksheet12
        return send_file(BytesIO(file_data), attachment_filename=student.rollno + "_12th Marksheet.pdf", as_attachment=True)
    else:
        flash("No file Exists")
        return redirect(url_for("feed", currentuser=current_user))


@app.route('/downloadmarksheet12mentor/<int:student_id>', methods=['GET', 'POST'])
def downloadmarksheet12mentor(student_id):
    student = Student.query.filter_by(id=student_id).first()
    if student.marksheet12:
        file_data = student.marksheet12
        return send_file(BytesIO(file_data), attachment_filename=student.rollno + "_12th Marksheet.pdf", as_attachment=True)
    else:
        flash("No file Exists")
        return render_template('student_info.html', student=student)


@app.route('/downloadmarksheet10/<int:student_id>', methods=['GET', 'POST'])
def downloadmarksheet10(student_id):
    student = Student.query.filter_by(id=student_id).first()
    if student.marksheet10:
        file_data = student.marksheet10
        return send_file(BytesIO(file_data), attachment_filename=student.rollno + "_10th Marksheet.pdf", as_attachment=True)
    else:
        flash("No file Exists")
        return redirect(url_for("feed", currentuser=current_user))


@app.route('/downloadmarksheet10mentor/<int:student_id>', methods=['GET', 'POST'])
def downloadmarksheet10mentor(student_id):
    student = Student.query.filter_by(id=student_id).first()
    if student.marksheet10:
        file_data = student.marksheet10
        return send_file(BytesIO(file_data), attachment_filename=student.rollno + "_10th Marksheet.pdf", as_attachment=True)
    else:
        flash("No file Exists")
        return render_template('student_info.html', student=student)


@app.route('/downloadmarksheetlastsem/<int:student_id>', methods=['GET', 'POST'])
def downloadmarksheetlastsem(student_id):
    student = Student.query.filter_by(id=student_id).first()
    if student.marksheetlastsem:
        file_data = student.marksheetlastsem
        return send_file(BytesIO(file_data), attachment_filename=student.rollno + "_LastSem Marksheet.pdf", as_attachment=True)
    else:
        flash("No file Exists")
        return redirect(url_for("feed", currentuser=current_user))


@app.route('/downloadmarksheetlastsemmentor/<int:student_id>', methods=['GET', 'POST'])
def downloadmarksheetlastsemmentor(student_id):
    student = Student.query.filter_by(id=student_id).first()
    if student.marksheetlastsem:
        file_data = student.marksheetlastsem
        return send_file(BytesIO(file_data), attachment_filename=student.rollno + "_LastSem Marksheet.pdf", as_attachment=True)
    else:
        flash("No file Exists")
        return render_template('student_info.html', student=student)


# Deleting the Documents

@app.route('/deletemarksheet12/<int:student_id>', methods=['POST'])
def deletemarksheet12(student_id):
    student = Student.query.filter_by(id=student_id).first()

    student.marksheet12name = None
    student.marksheet12 = None
    student.marksheet12verify = "Wait for Aunthentication"
    db.session.commit()
    flash("File Sucessfuly Deleted", "success")
    return redirect(url_for("feed", currentuser=current_user))


@app.route('/deletemarksheet12mentor/<int:student_id>', methods=['POST'])
def deletemarksheet12mentor(student_id):
    student = Student.query.filter_by(id=student_id).first()

    if student.marksheet12:
        student.marksheet12name = None
        student.marksheet12 = None
        student.marksheet12verify = "Wait for Aunthentication"
        db.session.commit()
        flash("File Sucessfuly Deleted", "success")
        return render_template('student_info.html', student=student)
    else:
        flash("No file Exists")
        return render_template('student_info.html', student=student)


@app.route('/deletemarksheet10/<int:student_id>', methods=['POST'])
def deletemarksheet10(student_id):
    student = Student.query.filter_by(id=student_id).first()
    if student.marksheet10:
        student.marksheet10name = None
        student.marksheet10 = None
        student.marksheet10verify = "Wait for Aunthentication"
        db.session.commit()
        flash("File Sucessfuly Deleted", "success")
        return redirect(url_for("feed", currentuser=current_user))


@app.route('/deletemarksheet10mentor/<int:student_id>', methods=['POST'])
def deletemarksheet10mentor(student_id):
    student = Student.query.filter_by(id=student_id).first()
    if student.marksheet10:
        student.marksheet10name = None
        student.marksheet10 = None
        student.marksheet10verify = "Wait for Aunthentication"
        db.session.commit()
        flash("File Sucessfuly Deleted", "success")
        return render_template('student_info.html', student=student)
    else:
        flash("No file Exists")
        return render_template('student_info.html', student=student)


@app.route('/deletemarksheetlastsem/<int:student_id>', methods=['POST'])
def deletemarksheetlastsem(student_id):
    student = Student.query.filter_by(id=student_id).first()

    if student.marksheetlastsem:
        student.marksheetlastsemname = None
        student.marksheetlastsem = None
        student.marksheetlastsemverify = "Wait for Aunthentication"
        db.session.commit()
        flash("File Sucessfuly Deleted", "success")
        return redirect(url_for("feed", currentuser=current_user))


@app.route('/deletemarksheetlastsemmentor/<int:student_id>', methods=['POST'])
def deletemarksheetlastsemmentor(student_id):
    student = Student.query.filter_by(id=student_id).first()
    if student.marksheetlastsem:
        student.marksheetlastsemname = None
        student.marksheetlastsem = None
        student.marksheetlastsemverify = "Wait for Aunthentication"
        db.session.commit()
        flash("File Sucessfuly Deleted", "success")
        return render_template('student_info.html', student=student)
    else:
        flash("No file Exists")
        return render_template('student_info.html', student=student)


# Buttons in Mentor Side
@app.route('/searchstudents/<int:mentorid>', methods=['POST'])
def search_student(mentorid):
    if request.method == "POST":
        search_string = request.form['search_string']
        search = "{0}".format(search_string)

        students = []

        results = Student.query.filter(or_(Student.fname.like(search), Student.mname.like(
            search), Student.sname.like(search), Student.rollno.like(search))).all()

        for x in results:
            if x.mentor_id == mentorid:
                students.append(x)

        if len(students) == 0:
            flash("No such student is registered to you")
        return render_template('mentor.html', results=students)


@app.route('/searchallstudents/<int:mentorid>', methods=['POST'])
def searchallstudents(mentorid):
    if request.method == 'POST':
        results = Student.query.filter_by(mentor_id=mentorid)
        return render_template('mentor.html', results=results)


@app.route('/studentinfo/<int:student_id>', methods=['POST', 'GET'])
def studentinfo(student_id):
    if request.method == "POST":
        student = Student.query.get_or_404(student_id)
        return render_template('student_info.html', student=student)
    return render_template("student_info.html")


# Updating student record on mentor side
@app.route('/mentoradd/<int:student_id>', methods=['POST'])
def mentoradd(student_id):
    if request.method == 'POST':
        student = Student.query.filter_by(id=student_id).first()

        student.fname = request.form.get("fname")
        student.mname = request.form.get("mname")
        student.sname = request.form.get("sname")
        student.rollno = request.form.get("rollno")
        student.dob = request.form.get("dob")
        student.age = request.form.get("age")
        student.gender = request.form.get("gender")
        student.mobno = request.form.get("mobno")
        student.email = request.form.get("email")
        student.dept = request.form.get("dept")
        student.div = request.form.get("div")
        student.yog = request.form.get("yog")
        student.batchno = request.form.get("batchno")

        student.cllg = request.form.get("cllg")
        student.cllgboard = request.form.get("cllgboard")
        student.marks12 = request.form.get("marks12")
        student.comp12 = request.form.get("comp12")

        student.school = request.form.get("school")
        student.schoolboard = request.form.get("schoolboard")
        student.marks10 = request.form.get("marks10")
        student.comp10 = request.form.get("comp10")

        student.certificate1verify = request.form.get("certificate1verify")
        student.certificate2verify = request.form.get("certificate2verify")
        student.certificate3verify = request.form.get("certificate3verify")
        student.certificate4verify = request.form.get("certificate4verify")
        student.certificate5verify = request.form.get("certificate5verify")

        student.marksheet12verify = request.form.get("12MSverify")
        student.marksheet10verify = request.form.get("10MSverify")
        student.marksheetlastsemverify = request.form.get("SEMMSverify")
        db.session.commit()
        flash("Student Details Updated", "success")
        return render_template('student_info.html', student=student)


@app.route('/deletestudent/<int:student_id>', methods=['POST'])
def deletestudent(student_id):
    if request.method == 'POST':
        student = Student.query.filter_by(id=student_id).first()
        db.session.delete(student)
        db.session.commit()
        flash("Student Record Successfully Deleted", "success")
        return render_template("mentor.html")
    return "Student Not Deleted"


@app.route('/detailspdf/<int:student_id>', methods=['POST', 'GET'])
def detailspdf(student_id):
    student = Student.query.get_or_404(student_id)
    css = ['details.css']
    rendered = render_template('detailspdf.html', student=student)
    pdf = pdfkit.from_string(rendered, False, css=css)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename = student.rollno +_Details.pdf'

    return response


# Uploading and Downloading Extra-curricular Certificates
@app.route('/uploadcertificate1/<int:student_id>', methods=["POST"])
@login_required
def uploadcertificate1(student_id):
    file = request.files['certificate1']
    print("got the file")
    student = Student.query.filter_by(id=student_id).first()
    print("got the row")
    student.certificate1name = file.filename
    student.certificate1 = file.read()
    print("added but not commimted")
    db.session.commit()
    print("added the marksheet")
    return redirect(url_for("feed", currentuser=current_user))


@app.route('/uploadcertificate2/<int:student_id>', methods=["POST"])
@login_required
def uploadcertificate2(student_id):
    file = request.files['certificate2']
    print("got the file")
    student = Student.query.filter_by(id=student_id).first()
    print("got the row")
    student.certificate2name = file.filename
    student.certificate2 = file.read()
    print("added but not commimted")
    db.session.commit()
    print("added the marksheet")
    return redirect(url_for("feed", currentuser=current_user))


@app.route('/uploadcertificate3/<int:student_id>', methods=["POST"])
@login_required
def uploadcertificate3(student_id):
    file = request.files['certificate3']
    print("got the file")
    student = Student.query.filter_by(id=student_id).first()
    print("got the row")
    student.certificate3name = file.filename
    student.certificate3 = file.read()
    print("added but not commimted")
    db.session.commit()
    print("added the marksheet")
    return redirect(url_for("feed", currentuser=current_user))


@app.route('/uploadcertificate4/<int:student_id>', methods=["POST"])
@login_required
def uploadcertificate4(student_id):
    file = request.files['certificate4']
    print("got the file")
    student = Student.query.filter_by(id=student_id).first()
    print("got the row")
    student.certificate4name = file.filename
    student.certificate4 = file.read()
    print("added but not commimted")
    db.session.commit()
    print("added the marksheet")
    return redirect(url_for("feed", currentuser=current_user))


@app.route('/uploadcertificate5/<int:student_id>', methods=["POST"])
@login_required
def uploadcertificate5(student_id):
    file = request.files['certificate5']
    print("got the file")
    student = Student.query.filter_by(id=student_id).first()
    print("got the row")
    student.certificate5name = file.filename
    student.certificate5 = file.read()
    print("added but not commimted")
    db.session.commit()
    print("added the marksheet")
    return redirect(url_for("feed", currentuser=current_user))


@app.route('/downloadcertificate1/<int:student_id>', methods=['POST'])
def downloadcertificate1(student_id):
    student = Student.query.filter_by(id=student_id).first()
    if len(student.certificate1name) > 1:
        file_data = student.certificate1
        return send_file(BytesIO(file_data), attachment_filename=student.rollno + "_Certificate1.pdf", as_attachment=True)
    else:
        flash("No file Exists")
        return redirect(url_for("feed", currentuser=current_user))


@app.route('/downloadcertificate1mentor/<int:student_id>', methods=['POST'])
def downloadcertificate1mentor(student_id):
    student = Student.query.filter_by(id=student_id).first()
    if student.certificate1:
        file_data = student.certificate1
        return send_file(BytesIO(file_data), attachment_filename=student.rollno + "_Certificate1.pdf", as_attachment=True)
    else:
        flash("No file Exists")
        return render_template('student_info.html', student=student)


@app.route('/downloadcertificate2/<int:student_id>', methods=['POST'])
def downloadcertificate2(student_id):
    student = Student.query.filter_by(id=student_id).first()
    if len(student.certificate2name) > 1:
        file_data = student.certificate2
        return send_file(BytesIO(file_data), attachment_filename=student.rollno + "_Certificate2.pdf", as_attachment=True)
    else:
        flash("No file Exists")
        return redirect(url_for("feed", currentuser=current_user))


@app.route('/downloadcertificate2mentor/<int:student_id>', methods=['POST'])
def downloadcertificate2mentor(student_id):
    student = Student.query.filter_by(id=student_id).first()
    if student.certificate2:
        file_data = student.certificate2
        return send_file(BytesIO(file_data), attachment_filename=student.rollno + "_Certificate2.pdf", as_attachment=True)
    else:
        flash("No file Exists")
        return render_template('student_info.html', student=student)


@app.route('/downloadcertificate3/<int:student_id>', methods=['POST'])
def downloadcertificate3(student_id):
    student = Student.query.filter_by(id=student_id).first()
    if len(student.certificate3name) > 1:
        file_data = student.certificate3
        return send_file(BytesIO(file_data), attachment_filename=student.rollno + "_Certificate3.pdf", as_attachment=True)
    else:
        flash("No file Exists")
        return redirect(url_for("feed", currentuser=current_user))


@app.route('/downloadcertificate3mentor/<int:student_id>', methods=['POST'])
def downloadcertificate3mentor(student_id):
    student = Student.query.filter_by(id=student_id).first()
    if student.certificate3:
        file_data = student.certificate3
        return send_file(BytesIO(file_data), attachment_filename=student.rollno + "_Certificate3.pdf", as_attachment=True)
    else:
        flash("No file Exists")
        return render_template('student_info.html', student=student)


@app.route('/downloadcertificate4/<int:student_id>', methods=['POST'])
def downloadcertificate4(student_id):
    student = Student.query.filter_by(id=student_id).first()
    if len(student.certificate4name) > 1:
        file_data = student.certificate4
        return send_file(BytesIO(file_data), attachment_filename=student.rollno + "_Certificate4.pdf", as_attachment=True)
    else:
        flash("No file Exists")
        return redirect(url_for("feed", currentuser=current_user))


@app.route('/downloadcertificate4mentor/<int:student_id>', methods=['POST'])
def downloadcertificate4mentor(student_id):
    student = Student.query.filter_by(id=student_id).first()
    if student.certificate4:
        file_data = student.certificate4
        return send_file(BytesIO(file_data), attachment_filename=student.rollno + "_Certificate4.pdf", as_attachment=True)
    else:
        flash("No file Exists")
        return render_template('student_info.html', student=student)


@app.route('/downloadcertificate5/<int:student_id>', methods=['POST'])
def downloadcertificate5(student_id):
    student = Student.query.filter_by(id=student_id).first()
    if len(student.certificate5name) > 1:
        file_data = student.certificate5
        return send_file(BytesIO(file_data), attachment_filename=student.rollno + "_Certificate5.pdf", as_attachment=True)
    else:
        flash("No file Exists")
        return redirect(url_for("feed", currentuser=current_user))


@app.route('/downloadcertificate5mentor/<int:student_id>', methods=['POST'])
def downloadcertificate5mentor(student_id):
    student = Student.query.filter_by(id=student_id).first()
    if student.certificate5:
        file_data = student.certificate5
        return send_file(BytesIO(file_data), attachment_filename=student.rollno + "_Certificate5.pdf", as_attachment=True)
    else:
        flash("No file Exists")
        return render_template('student_info.html', student=student)


@app.route('/deletecertificate1/<int:student_id>', methods=['POST'])
def deletecertificate1(student_id):
    student = Student.query.filter_by(id=student_id).first()
    student.certificate1name = None
    student.certificate1 = None
    student.certificate1verify == "Wait for Aunthentication"
    db.session.commit()
    flash("File Sucessfuly Deleted", "success")
    return redirect(url_for("feed", currentuser=current_user))


@app.route('/deletecertificate1mentor/<int:student_id>', methods=['POST'])
def deletecertificate1mentor(student_id):
    student = Student.query.filter_by(id=student_id).first()
    if student.certificate1:
        student.certificate1name = None
        student.certificate1 = None
        student.certificate1verify == "Wait for Aunthentication"
        db.session.commit()
        flash("File Sucessfuly Deleted", "success")
        return render_template('student_info.html', student=student)
    else:
        flash("No file Exists")
        return render_template('student_info.html', student=student)


@app.route('/deletecertificate2/<int:student_id>', methods=['POST'])
def deletecertificate2(student_id):
    student = Student.query.filter_by(id=student_id).first()
    student.certificate2name = None
    student.certificate2 = None
    student.certificate2verify == "Wait for Aunthentication"
    db.session.commit()
    flash("File Sucessfuly Deleted", "success")
    return redirect(url_for("feed", currentuser=current_user))


@app.route('/deletecertificate2mentor/<int:student_id>', methods=['POST'])
def deletecertificate2mentor(student_id):
    student = Student.query.filter_by(id=student_id).first()
    if student.certificate2:
        student.certificate2name = None
        student.certificate2 = None
        student.certificate2verify == "Wait for Aunthentication"
        db.session.commit()
        flash("File Sucessfuly Deleted", "success")
        return render_template('student_info.html', student=student)
    else:
        flash("No file Exists")
        return render_template('student_info.html', student=student)


@app.route('/deletecertificate3/<int:student_id>', methods=['POST'])
def deletecertificate3(student_id):
    student = Student.query.filter_by(id=student_id).first()
    student.certificate3name = None
    student.certificate3 = None
    student.certificate3verify == "Wait for Aunthentication"
    db.session.commit()
    flash("File Sucessfuly Deleted", "success")
    return redirect(url_for("feed", currentuser=current_user))


@app.route('/deletecertificate3mentor/<int:student_id>', methods=['POST'])
def deletecertificate3mentor(student_id):
    student = Student.query.filter_by(id=student_id).first()
    if student.certificate3:
        student.certificate3name = None
        student.certificate3 = None
        student.certificate3verify == "Wait for Aunthentication"
        db.session.commit()
        flash("File Sucessfuly Deleted", "success")
        return render_template('student_info.html', student=student)
    else:
        flash("No file Exists")
        return render_template('student_info.html', student=student)


@app.route('/deletecertificate4/<int:student_id>', methods=['POST'])
def deletecertificate4(student_id):
    student = Student.query.filter_by(id=student_id).first()
    student.certificate4name = None
    student.certificate4 = None
    student.certificate4verify == "Wait for Aunthentication"
    db.session.commit()
    flash("File Sucessfuly Deleted", "success")
    return redirect(url_for("feed", currentuser=current_user))


@app.route('/deletecertificate4mentor/<int:student_id>', methods=['POST'])
def deletecertificate4mentor(student_id):
    student = Student.query.filter_by(id=student_id).first()
    if student.certificate4:
        student.certificate4name = None
        student.certificate4 = None
        student.certificate4verify == "Wait for Aunthentication"
        db.session.commit()
        flash("File Sucessfuly Deleted", "success")
        return render_template('student_info.html', student=student)
    else:
        flash("No file Exists")
        return render_template('student_info.html', student=student)


@app.route('/deletecertificate5/<int:student_id>', methods=['POST'])
def deletecertificate5(student_id):
    student = Student.query.filter_by(id=student_id).first()
    student.certificate5name = None
    student.certificate5 = None
    student.certificate5verify == "Wait for Aunthentication"
    db.session.commit()
    flash("File Sucessfuly Deleted", "success")
    return redirect(url_for("feed", currentuser=current_user))


@app.route('/deletecertificate5mentor/<int:student_id>', methods=['POST'])
def deletecertificate5mentor(student_id):
    student = Student.query.filter_by(id=student_id).first()
    if student.certificate5:
        student.certificate5name = None
        student.certificate5 = None
        student.certificate5verify == "Wait for Aunthentication"
        db.session.commit()
        flash("File Sucessfuly Deleted", "success")
        return render_template('student_info.html', student=student)
    else:
        flash("No file Exists")
        return render_template('student_info.html', student=student)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
