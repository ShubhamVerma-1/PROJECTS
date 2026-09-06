from flask import render_template, request , redirect , url_for, flash , session
from app import app
from models import db, User, StudentProfile, CompanyProfile, PlacementDrive, Application
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, date


#                                              A U T H O R I Z A T I O N

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Email does not exist")
            return redirect(url_for('login'))

        if not check_password_hash(user.password_hash, password):
            flash("Incorrect password")
            return redirect(url_for('login'))

        if not user.is_active:
            flash("Your account has been deactivated")
            return redirect(url_for("login"))

        if user.role == 'company':
            if user.company_profile.approval_status != 'Approved':
                flash("Login Failed: Admin approval pending")
                return redirect(url_for('login'))

        session['user_id'] = user.id
        session['role'] = user.role

        if user.role == 'admin':
            return redirect(url_for('admin_profile'))
        elif user.role == 'company':
            return redirect(url_for('company_profile'))
        else:
            return redirect(url_for('student_profile'))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logout Successful")
    return redirect(url_for('login'))

@app.route("/register")
def register():
    return render_template("register.html")


#                                             S T U D E N T

@app.route("/register_student", methods=["GET", "POST"])
def register_student():
    if request.method == "POST":
        email = request.form.get("email")
        name = request.form.get("name")
        qualification = request.form.get("qualification")
        resume = request.form.get("resume")
        password = request.form.get("password")

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email id already exist")
            return redirect(url_for('register_student'))

        hashed_pass = generate_password_hash(password)

        new_user = User(email=email, name=name, password_hash=hashed_pass, role='student')
        new_profile = StudentProfile(qualification=qualification, resume_link=resume)
        new_user.student_profile = new_profile

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! You can now log in.")
        return redirect(url_for('login'))

    return render_template("register_student.html")


def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'student':
            flash("Student access only.")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/student_profile")
@student_required
def student_profile():
    user = User.query.get(session['user_id'])

    # Only approved drives visible to students
    drives = PlacementDrive.query.filter_by(status='Approved').filter(
    PlacementDrive.deadline >= date.today()).all()

    applications = Application.query.filter_by(student_id=user.id).all()

    # Build a set of drive IDs the student has already applied to
    applied_drive_ids = {app.drive_id for app in applications}

    return render_template(
        "student_profile.html",
        user=user,
        drives=drives,
        applications=applications,
        applied_drive_ids=applied_drive_ids
    )


@app.route("/drive_detail/<int:drive_id>")
@student_required
def drive_detail(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)

    student_id = session.get('user_id')
    already_applied = Application.query.filter_by(
        student_id=student_id,
        drive_id=drive_id
    ).first() is not None

    return render_template(
        "drive_detail.html",
        drive=drive,
        already_applied=already_applied,
        today=date.today()
    )


@app.route("/profile_update", methods=["GET", "POST"])
@student_required
def profile_update():
    student_id = session.get('user_id')
    profile = StudentProfile.query.filter_by(student_id=student_id).first()
    user = User.query.filter_by(id=student_id).first()

    if request.method == "POST":
        user.name = request.form.get("name")
        profile.qualification = request.form.get("qualification")
        profile.resume_link = request.form.get("resume")

        db.session.commit()
        flash("Profile updated successfully!")
        return redirect(url_for('student_profile'))

    return render_template("profile_update.html", profile=profile, user=user)


@app.route("/apply_drive/<int:drive_id>")
@student_required
def apply_drive(drive_id):
    student_id = session.get("user_id")

    # Check if already applied
    existing_application = Application.query.filter_by(
        student_id=student_id,
        drive_id=drive_id
    ).first()

    if existing_application:
        flash("You have already applied for this drive.")
        return redirect(url_for("student_profile"))

    # Check if the deadline has passed
    drive = PlacementDrive.query.get_or_404(drive_id)
    if drive.deadline < date.today():
        flash("The application deadline for this drive has passed.")
        return redirect(url_for("student_profile"))

    new_application = Application(
        student_id=student_id,
        drive_id=drive_id
    )

    db.session.add(new_application)
    db.session.commit()

    flash("Application submitted successfully.")
    return redirect(url_for("student_profile"))


#                             C O M P A N Y

@app.route("/register_company", methods=["GET", "POST"])
def register_company():
    if request.method == "POST":
        email = request.form.get("email")
        name = request.form.get("company_name")
        website = request.form.get("company_website")
        contact = request.form.get("hr_contact")
        password = request.form.get("password")

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email id already exist")
            return redirect(url_for('register_company'))

        hashed_pass = generate_password_hash(password)

        new_user = User(email=email, name=name, password_hash=hashed_pass, role='company')
        new_profile = CompanyProfile(company_website=website, company_hr_contact=contact)
        new_user.company_profile = new_profile

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! You can now log in.")
        return redirect(url_for('login'))

    return render_template("register_company.html")


def company_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'company':
            flash("Company access only.")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/company_profile")
@company_required
def company_profile():
    user = User.query.get(session['user_id'])
    company_profile = user.company_profile

    drives = PlacementDrive.query.filter_by(company_id=user.id).all()

    drive_data = []
    for drive in drives:
        applicant_count = Application.query.filter_by(drive_id=drive.drive_id).count()
        drive_data.append({
            "drive": drive,
            "applicant_count": applicant_count
        })

    return render_template(
        "company_profile.html",
        user=user,
        company_profile=company_profile,
        drive_data=drive_data
    )


@app.route("/drive_creation", methods=["GET", "POST"])
@company_required
def drive_creation():
    if request.method == "POST":
        drive_name = request.form.get("drive_name")
        job_title = request.form.get("job_title")
        job_description = request.form.get("job_description")
        salary = request.form.get("salary")
        location = request.form.get("location")
        eligibility = request.form.get("eligibility")
        deadline = datetime.strptime(request.form.get("deadline"), '%Y-%m-%d').date()

        current_company_id = session.get('user_id')

        new_drive = PlacementDrive(
            company_id=current_company_id,
            drive_name=drive_name,
            job_title=job_title,
            job_description=job_description,
            salary=salary,
            location=location,
            eligibility=eligibility,
            deadline=deadline
        )

        db.session.add(new_drive)
        db.session.commit()

        flash("Placement Drive created successfully! Admin approval pending")
        return redirect(url_for('company_profile'))

    return render_template("drive_creation.html", drive=None)


@app.route("/close_drive/<int:drive_id>")
@company_required
def close_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = "Closed"
    db.session.commit()
    flash("Drive closed successfully")
    return redirect(url_for("company_profile"))


@app.route("/delete_drive/<int:drive_id>")
@company_required
def delete_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    db.session.delete(drive)
    db.session.commit()
    flash("Drive deleted")
    return redirect(url_for("company_profile"))


@app.route("/view_applicants/<int:drive_id>")
@company_required
def view_applicants(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)

    if drive.company_id != session.get('user_id'):
        flash("Unauthorized access.")
        return redirect(url_for('company_profile'))

    applications = Application.query.filter_by(drive_id=drive_id).all()

    return render_template(
        "view_applicants.html",
        drive=drive,
        applications=applications
    )


@app.route("/update_application_status/<int:app_id>/<status>")
@company_required
def update_application_status(app_id, status):
    # FIX 5: Validate status value before applying it
    allowed_statuses = {'Shortlisted', 'Selected', 'Rejected'}
    if status not in allowed_statuses:
        flash("Invalid status value.")
        return redirect(url_for('company_profile'))

    application = Application.query.get_or_404(app_id)
    application.status = status
    db.session.commit()

    flash("Application status updated.")
    return redirect(url_for('view_applicants', drive_id=application.drive_id))


@app.route("/edit_drive/<int:drive_id>", methods=["GET", "POST"])
@company_required
def edit_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)

    if drive.company_id != session.get('user_id'):
        flash("Unauthorized access.")
        return redirect(url_for('company_profile'))

    if request.method == "POST":
        drive.drive_name = request.form.get("drive_name")
        drive.job_title = request.form.get("job_title")
        drive.job_description = request.form.get("job_description")
        drive.salary = request.form.get("salary")
        drive.location = request.form.get("location")
        drive.eligibility = request.form.get("eligibility")
        drive.deadline = datetime.strptime(request.form.get("deadline"), '%Y-%m-%d').date()
        drive.status = 'Pending'

        db.session.commit()
        flash("Drive updated successfully! Pending admin re-approval.")
        return redirect(url_for('company_profile'))

    return render_template("drive_creation.html", drive=drive)


#                                           A D M I N

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash("Unauthorized Access. Admin privileges required.")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/admin_profile")
@admin_required
def admin_profile():
    user = User.query.get(session['user_id'])

    total_students = User.query.filter_by(role='student').count()
    total_companies = User.query.filter_by(role='company').count()
    total_drives = PlacementDrive.query.count()
    total_applications = Application.query.count()

    pending_companies = CompanyProfile.query.filter_by(approval_status='Pending').all()
    pending_drives = PlacementDrive.query.filter_by(status='Pending').all()

    return render_template(
        "admin_profile.html",
        user=user,
        total_students=total_students,
        total_companies=total_companies,
        total_drives=total_drives,
        total_applications=total_applications,
        pending_companies=pending_companies,
        pending_drives=pending_drives
    )


@app.route("/approve_company/<int:id>")
@admin_required
def approve_company(id):
    company = CompanyProfile.query.get(id)
    company.approval_status = "Approved"
    db.session.commit()
    flash("Company Approved")
    return redirect(url_for('admin_profile'))


@app.route("/reject_company/<int:id>")
@admin_required
def reject_company(id):
    company = CompanyProfile.query.get(id)
    company.approval_status = "Rejected"
    db.session.commit()
    flash("Company Rejected")
    return redirect(url_for('admin_profile'))


@app.route("/approve_drive/<int:id>")
@admin_required
def approve_drive(id):
    drive = PlacementDrive.query.get(id)
    drive.status = "Approved"
    db.session.commit()
    flash("Drive Approved")
    return redirect(url_for('admin_profile'))


@app.route("/reject_drive/<int:id>")
@admin_required
def reject_drive(id):
    drive = PlacementDrive.query.get(id)
    drive.status = "Rejected"
    db.session.commit()
    flash("Drive Rejected")
    return redirect(url_for('admin_profile'))


@app.route("/blacklist_user/<int:user_id>")
@admin_required
def blacklist_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = False
    db.session.commit()
    flash("User account deactivated")
    return redirect(url_for("admin_students"))


# reactivate route
@app.route("/reactivate_user/<int:user_id>")
@admin_required
def reactivate_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = True
    db.session.commit()
    flash("User account reactivated")
    return redirect(url_for("admin_students"))


@app.route("/admin/companies")
@admin_required
def admin_companies():
    companies = CompanyProfile.query.all()
    return render_template("admin_companies.html", companies=companies)


@app.route("/admin/students")
@admin_required
def admin_students():
    students = StudentProfile.query.all()
    return render_template("admin_students.html", students=students)


@app.route("/admin/drives")
@admin_required
def admin_drives():
    drives = PlacementDrive.query.all()
    return render_template("admin_drives.html", drives=drives)


@app.route("/admin/applications")
@admin_required
def admin_applications():
    applications = Application.query.all()
    return render_template("admin_applications.html", applications=applications)


#  Search routes query StudentProfile/CompanyProfile directly
@app.route("/search_students")
@admin_required
def search_students():
    query = request.args.get("q", "")
    students = StudentProfile.query.join(User).filter(
        User.name.ilike(f"%{query}%")
    ).all()
    return render_template("admin_students.html", students=students)


@app.route("/search_companies")
@admin_required
def search_companies():
    query = request.args.get("q", "")
    companies = CompanyProfile.query.join(User).filter(
        User.name.ilike(f"%{query}%")
    ).all()
    return render_template("admin_companies.html", companies=companies)