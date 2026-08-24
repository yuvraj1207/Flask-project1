from datetime import datetime
from models import db


class Course(db.Model):
    __tablename__ = "courses"

    id            = db.Column(db.Integer, primary_key=True)
    title         = db.Column(db.String(200), nullable=False)
    description   = db.Column(db.Text)
    instructor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    modules     = db.relationship("Module",     backref="course", lazy=True, cascade="all, delete-orphan")
    enrollments = db.relationship("Enrollment", backref="course", lazy=True, cascade="all, delete-orphan")
    materials   = db.relationship("Material",   backref="course", lazy=True, cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id":            self.id,
            "title":         self.title,
            "description":   self.description,
            "instructor_id": self.instructor_id,
            "created_at":    self.created_at.isoformat() if self.created_at else None,
        }


class Module(db.Model):
    __tablename__ = "modules"

    id          = db.Column(db.Integer, primary_key=True)
    course_id   = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    title       = db.Column(db.String(200), nullable=False)
    order_index = db.Column(db.Integer, default=0)

    lessons   = db.relationship("Lesson",   backref="module", lazy=True, cascade="all, delete-orphan")
    materials = db.relationship("Material", backref="module", lazy=True, cascade="all, delete-orphan")
    quizzes   = db.relationship("Quiz",     backref="module", lazy=True, cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id":          self.id,
            "course_id":   self.course_id,
            "title":       self.title,
            "order_index": self.order_index,
        }


class Lesson(db.Model):
    __tablename__ = "lessons"

    id          = db.Column(db.Integer, primary_key=True)
    module_id   = db.Column(db.Integer, db.ForeignKey("modules.id"), nullable=False)
    title       = db.Column(db.String(200), nullable=False)
    content     = db.Column(db.Text)
    order_index = db.Column(db.Integer, default=0)

    def to_dict(self) -> dict:
        return {
            "id":          self.id,
            "module_id":   self.module_id,
            "title":       self.title,
            "content":     self.content,
            "order_index": self.order_index,
        }
