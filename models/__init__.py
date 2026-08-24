from config.database import db  # noqa: F401

# Import all models so SQLAlchemy registers their metadata before db.create_all()
from models.user import User          # noqa: F401
from models.course import Course, Module, Lesson  # noqa: F401
from models.enrollment import Enrollment          # noqa: F401
from models.quiz import Quiz, Question, QuizResult  # noqa: F401
from models.material import Material              # noqa: F401
