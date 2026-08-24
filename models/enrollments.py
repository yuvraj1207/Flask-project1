from config.database import db
from datetime import datetime

class Enrollment(db.Model):
    __tablename__ = 'enrollments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime)
    progress_percentage = db.Column(db.Float, default=0.0)

    __table_args__ = (db.UniqueConstraint('student_id', 'course_id', name='unique_student_course'),)