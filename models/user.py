from config.database import db
from datetime  import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('Student', 'Instructor', 'Admin'), default='Student', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime)

    # Relationships
    enrollments = db.relationship('Enrollment', backref='student', lazy=True, cascade="all, delete-orphan")
    quiz_results = db.relationship('QuizResult', backref='student', lazy=True, cascade="all, delete-orphan")
    created_courses = db.relationship('Course', backref='instructor', lazy=True)