from datetime import datetime
from models import db


class Quiz(db.Model):
    __tablename__ = "quizzes"

    id           = db.Column(db.Integer, primary_key=True)
    module_id    = db.Column(db.Integer, db.ForeignKey("modules.id"), nullable=False)
    title        = db.Column(db.String(200), nullable=False)
    pass_percent = db.Column(db.Float, default=50.0)

    questions = db.relationship("Question",   backref="quiz", lazy=True, cascade="all, delete-orphan")
    results   = db.relationship("QuizResult", backref="quiz", lazy=True, cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id":           self.id,
            "module_id":    self.module_id,
            "title":        self.title,
            "pass_percent": self.pass_percent,
        }


class Question(db.Model):
    __tablename__ = "questions"

    id             = db.Column(db.Integer, primary_key=True)
    quiz_id        = db.Column(db.Integer, db.ForeignKey("quizzes.id"), nullable=False)
    text           = db.Column(db.Text,        nullable=False)
    option_a       = db.Column(db.String(255))
    option_b       = db.Column(db.String(255))
    option_c       = db.Column(db.String(255))
    option_d       = db.Column(db.String(255))
    correct_option = db.Column(db.String(1),   nullable=False)  # 'a' | 'b' | 'c' | 'd'
    points         = db.Column(db.Integer, default=1)

    def __getitem__(self, key):
        return getattr(self, key, None)

    def to_dict(self, reveal_answer: bool = False) -> dict:
        data = {
            "id":      self.id,
            "quiz_id": self.quiz_id,
            "text":    self.text,
            "options": {
                "a": self.option_a,
                "b": self.option_b,
                "c": self.option_c,
                "d": self.option_d,
            },
            "points": self.points,
        }
        if reveal_answer:
            data["correct_option"] = self.correct_option
        return data


class QuizResult(db.Model):
    __tablename__ = "quiz_results"

    id           = db.Column(db.Integer, primary_key=True)
    quiz_id      = db.Column(db.Integer, db.ForeignKey("quizzes.id"), nullable=False)
    student_id   = db.Column(db.Integer, db.ForeignKey("users.id"),   nullable=False)
    score        = db.Column(db.Float,   nullable=False)
    total        = db.Column(db.Float,   nullable=False)
    percent      = db.Column(db.Float,   nullable=False)
    passed       = db.Column(db.Boolean, default=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id":           self.id,
            "quiz_id":      self.quiz_id,
            "student_id":   self.student_id,
            "score":        self.score,
            "total":        self.total,
            "percent":      self.percent,
            "passed":       self.passed,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
        }
