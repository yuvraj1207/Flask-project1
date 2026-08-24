from datetime import datetime
from models import db


class Enrollment(db.Model):
    __tablename__ = "enrollments"
    __table_args__ = (
        db.UniqueConstraint("student_id", "course_id", name="uq_student_course"),
    )

    id                = db.Column(db.Integer, primary_key=True)
    student_id        = db.Column(db.Integer, db.ForeignKey("users.id"),   nullable=False)
    course_id         = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    enrolled_at       = db.Column(db.DateTime, default=datetime.utcnow)
    progress_percent  = db.Column(db.Float, default=0.0)
    completed_lessons = db.Column(db.Text, default="")  # comma-separated lesson IDs

    def to_dict(self) -> dict:
        return {
            "id":               self.id,
            "student_id":       self.student_id,
            "course_id":        self.course_id,
            "progress_percent": self.progress_percent,
            "enrolled_at":      self.enrolled_at.isoformat() if self.enrolled_at else None,
        }
