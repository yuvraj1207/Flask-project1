from config.database import db
from models.enrollments import Enrollment

class EnrollmentDAO:
    @staticmethod
    def enroll_student(student_id, course_id):
        # Prevent duplicate enrollment
        existing = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
        if existing:
            return existing

        enrollment = Enrollment(student_id=student_id, course_id=course_id)
        db.session.add(enrollment)
        db.session.commit()
        return enrollment

    @staticmethod
    def get_enrollment(student_id, course_id):
        return Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()

    @staticmethod
    def get_student_enrollments(student_id):
        return Enrollment.query.filter_by(student_id=student_id).all()

    @staticmethod
    def update_progress(student_id, course_id, progress_percentage):
        enrollment = EnrollmentDAO.get_enrollment(student_id, course_id)
        if enrollment:
            enrollment.progress_percentage = progress_percentage
            db.session.commit()
        return enrollment