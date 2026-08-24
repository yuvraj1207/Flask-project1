from datetime import datetime
from models import db


class Material(db.Model):
    __tablename__ = "materials"

    id          = db.Column(db.Integer, primary_key=True)
    course_id   = db.Column(db.Integer, db.ForeignKey("courses.id"),        nullable=False)
    module_id   = db.Column(db.Integer, db.ForeignKey("modules.id"),        nullable=True)
    filename    = db.Column(db.String(255), nullable=False)
    stored_path = db.Column(db.String(500), nullable=False)   # relative path under static/uploads
    file_type   = db.Column(db.String(20),  nullable=False)   # pdf | image | video | doc
    size_bytes  = db.Column(db.Integer, default=0)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id":          self.id,
            "course_id":   self.course_id,
            "module_id":   self.module_id,
            "filename":    self.filename,
            "stored_path": self.stored_path,
            "file_type":   self.file_type,
            "size_bytes":  self.size_bytes,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
        }
