from config.database import db
from datetime import datetime


class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)

    instructor_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime
    )


class Module(db.Model):
    __tablename__ = 'modules'

    id = db.Column(db.Integer, primary_key=True)

    course_id = db.Column(
        db.Integer,
        db.ForeignKey('courses.id'),
        nullable=False
    )

    title = db.Column(
        db.String(150),
        nullable=False
    )

    order = db.Column(
        db.Integer,
        default=1
    )


class Lesson(db.Model):
    __tablename__ = 'lessons'

    id = db.Column(db.Integer, primary_key=True)

    module_id = db.Column(
        db.Integer,
        db.ForeignKey('modules.id'),
        nullable=False
    )

    title = db.Column(
        db.String(150),
        nullable=False
    )

    content = db.Column(
        db.Text,
        nullable=True
    )

    video_url = db.Column(
        db.String(255),
        nullable=True
    )


class Material(db.Model):
    __tablename__ = 'materials'

    id = db.Column(db.Integer, primary_key=True)

    course_id = db.Column(db.Integer,db.ForeignKey('courses.id'),nullable=False)

    file_name = db.Column(db.String(255),)

    file_path = db.Column(db.String(255),nullable=False)

    file_type = db.Column(db.String(50),nullable=False)
    file_size_bytes = db.Column(db.Integer,nullable=False)
    uploaded_at = db.Column(db.DateTime,default=datetime)