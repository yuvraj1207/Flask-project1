from sqlalchemy.exc import SQLAlchemyError
from models import db
from models.enrollment import Enrollment
from dao.user_dao import DAOError


class EnrollmentDAO:

    @staticmethod
    def create(student_id: int, course_id: int) -> Enrollment:
        try:
            enrollment = Enrollment(student_id=student_id, course_id=course_id)
            db.session.add(enrollment)
            db.session.commit()
            return enrollment
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise DAOError(f"Failed to create enrollment: {exc}") from exc

    @staticmethod
    def get(enrollment_id: int):
        try:
            return db.session.get(Enrollment, enrollment_id)
        except SQLAlchemyError as exc:
            raise DAOError(f"Failed to fetch enrollment: {exc}") from exc

    @staticmethod
    def get_by_student_and_course(student_id: int, course_id: int):
        try:
            return Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
        except SQLAlchemyError as exc:
            raise DAOError(f"Failed to fetch enrollment: {exc}") from exc

    @staticmethod
    def get_for_student(student_id: int):
        try:
            return Enrollment.query.filter_by(student_id=student_id).all()
        except SQLAlchemyError as exc:
            raise DAOError(f"Failed to list enrollments for student: {exc}") from exc

    @staticmethod
    def get_for_course(course_id: int):
        try:
            return Enrollment.query.filter_by(course_id=course_id).all()
        except SQLAlchemyError as exc:
            raise DAOError(f"Failed to list enrollments for course: {exc}") from exc

    @staticmethod
    def update_progress(enrollment: Enrollment, progress_percent: float, completed_lessons: str) -> Enrollment:
        try:
            enrollment.progress_percent  = progress_percent
            enrollment.completed_lessons = completed_lessons
            db.session.commit()
            return enrollment
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise DAOError(f"Failed to update progress: {exc}") from exc

    @staticmethod
    def delete(enrollment: Enrollment) -> None:
        try:
            db.session.delete(enrollment)
            db.session.commit()
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise DAOError(f"Failed to delete enrollment: {exc}") from exc
