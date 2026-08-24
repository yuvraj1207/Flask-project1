from dao.course_dao import CourseDAO
from dao.enrollment_dao import EnrollmentDAO
from dao.quiz_dao import QuizDAO
from dao.user_dao import DAOError


class ProgressServiceError(Exception):
    """Raised for all progress business-logic failures."""


class ProgressService:

    @staticmethod
    def _all_lesson_ids_for_course(course_id: int) -> list:
        """Return a list of all lesson IDs that belong to a course."""
        try:
            lesson_ids = []
            for module in CourseDAO.get_modules_for_course(course_id):
                for lesson in CourseDAO.get_lessons_for_module(module.id):
                    lesson_ids.append(lesson.id)
            return lesson_ids
        except DAOError as exc:
            raise ProgressServiceError(str(exc)) from exc

    @staticmethod
    def mark_lesson_complete(student_id: int, course_id: int, lesson_id: int):
        """
        Mark a lesson complete for a student and recalculate progress %.
        Raises ProgressServiceError if student is not enrolled.
        """
        try:
            enrollment = EnrollmentDAO.get_by_student_and_course(student_id, course_id)
        except DAOError as exc:
            raise ProgressServiceError(str(exc)) from exc

        if not enrollment:
            raise ProgressServiceError("Student is not enrolled in this course.")

        completed = set(filter(None, (enrollment.completed_lessons or "").split(",")))
        completed.add(str(lesson_id))

        all_lesson_ids = ProgressService._all_lesson_ids_for_course(course_id)
        total          = len(all_lesson_ids)
        progress_pct   = round((len(completed) / total) * 100, 2) if total else 0.0

        try:
            EnrollmentDAO.update_progress(enrollment, progress_pct, ",".join(sorted(completed)))
        except DAOError as exc:
            raise ProgressServiceError(str(exc)) from exc

        return enrollment

    @staticmethod
    def get_progress(student_id: int, course_id: int):
        """Return the Enrollment (which carries progress_percent). Raises if not enrolled."""
        try:
            enrollment = EnrollmentDAO.get_by_student_and_course(student_id, course_id)
        except DAOError as exc:
            raise ProgressServiceError(str(exc)) from exc

        if not enrollment:
            raise ProgressServiceError("Student is not enrolled in this course.")

        return enrollment

    @staticmethod
    def get_learning_history(student_id: int) -> dict:
        """Return all enrollments and quiz results for a student."""
        try:
            enrollments  = EnrollmentDAO.get_for_student(student_id)
            quiz_results = QuizDAO.get_results_for_student(student_id)
        except DAOError as exc:
            raise ProgressServiceError(str(exc)) from exc

        return {
            "enrollments":  enrollments,
            "quiz_results": quiz_results,
        }
