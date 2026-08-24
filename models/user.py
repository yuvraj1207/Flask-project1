from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from models import db


class User(db.Model):
    __tablename__ = "users"

    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(120), nullable=False)
    email        = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role         = db.Column(db.String(20), nullable=False, default="student")  # student | instructor | admin
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    courses      = db.relationship(
        "Course", backref="instructor", lazy=True,
        foreign_keys="Course.instructor_id",
        cascade="all, delete-orphan"
    )
    enrollments  = db.relationship("Enrollment", backref="student", lazy=True, cascade="all, delete-orphan")
    quiz_results = db.relationship("QuizResult", backref="student", lazy=True, cascade="all, delete-orphan")

    # ------------------------------------------------------------------
    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        return {
            "id":         self.id,
            "name":       self.name,
            "email":      self.email,
            "role":       self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
