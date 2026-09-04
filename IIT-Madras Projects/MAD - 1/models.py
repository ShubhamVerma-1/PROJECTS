from app import app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash , check_password_hash
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'Admin', 'Company', or 'Student'
    is_active = db.Column(db.Boolean, default=True) # for Blacklisting/Deactivation

    company_profile = db.relationship('CompanyProfile', backref='user_account', uselist=False, cascade="all, delete-orphan")
    student_profile = db.relationship('StudentProfile', backref='user_account', uselist=False, cascade="all, delete-orphan")


class CompanyProfile(db.Model):
    __tablename__ = 'company_profiles'

    company_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    company_website = db.Column(db.Text)
    company_hr_contact = db.Column(db.String(30),nullable=True)
    approval_status = db.Column(db.String(20), default='Pending')

    drives = db.relationship('PlacementDrive', backref='company', lazy=True, cascade="all, delete-orphan")

class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'

    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    qualification = db.Column(db.String(100))
    resume_link = db.Column(db.Text)   

    applications = db.relationship('Application', backref='student', lazy=True, cascade="all, delete-orphan") 

class PlacementDrive(db.Model):
    __tablename__ = 'placement_drives'

    drive_id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company_profiles.company_id'), nullable=False)
    drive_name = db.Column(db.String(100), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    salary = db.Column(db.String(50))
    location = db.Column(db.String(100))
    eligibility = db.Column(db.Text)
    deadline = db.Column(db.Date, nullable=False)  

    # Admin manages this status
    status = db.Column(db.String(20), default='Pending') # 'Pending', 'Approved', 'Rejected', 'Closed'
    
    # 1:N Relationship - One drive has many applications
    applications = db.relationship('Application', backref='drive', lazy=True, cascade="all, delete-orphan")  

class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.student_id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drives.drive_id'), nullable=False)
    
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Applied') # 'Applied', 'Shortlisted', 'Waiting', 'Rejected' 

    __table_args__ = (
        db.UniqueConstraint('student_id', 'drive_id', name='unique_student_application'),
    )

with app.app_context():
        db.create_all()
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            password_hash = generate_password_hash('admin')
            admin = User(email='admin@1',name="Admin",password_hash=password_hash,role='admin')
            db.session.add(admin)
            db.session.commit()
