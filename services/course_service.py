from dao.course_dao import CourseDAO
from dao.enrollment_dao import EnrollmentDAO
from dao.user_dao import DAOError


class CourseServiceError(Exception):
    """Raised for all course / module / lesson business-logic failures."""


class CourseService:

    # ── Courses ──────────────────────────────────────────────────────
    @staticmethod
    def create_course(title: str, description: str, instructor_id: int):
        if not title or not title.strip():
            raise CourseServiceError("Course title is required.")
        try:
            return CourseDAO.create_course(title.strip(), description, instructor_id)
        except DAOError as exc:
            raise CourseServiceError(str(exc)) from exc

    @staticmethod
    def get_course(course_id: int):
        try:
            course = CourseDAO.get_course(course_id)
        except DAOError as exc:
            raise CourseServiceError(str(exc)) from exc
        if not course:
            raise CourseServiceError("Course not found.")
        return course

    @staticmethod
    def list_courses():
        try:
            return CourseDAO.get_all_courses()
        except DAOError as exc:
            raise CourseServiceError(str(exc)) from exc

    @staticmethod
    def list_courses_for_instructor(instructor_id: int):
        try:
            return CourseDAO.get_courses_by_instructor(instructor_id)
        except DAOError as exc:
            raise CourseServiceError(str(exc)) from exc

    @staticmethod
    def update_course(course_id: int, **kwargs):
        course = CourseService.get_course(course_id)
        try:
            return CourseDAO.update_course(course, **kwargs)
        except DAOError as exc:
            raise CourseServiceError(str(exc)) from exc

    @staticmethod
    def delete_course(course_id: int) -> None:
        course = CourseService.get_course(course_id)
        try:
            CourseDAO.delete_course(course)
        except DAOError as exc:
            raise CourseServiceError(str(exc)) from exc

    # ── Modules ───────────────────────────────────────────────────────
    @staticmethod
    def add_module(course_id: int, title: str, order_index: int = 0):
        CourseService.get_course(course_id)          # ensures course exists
        if not title or not title.strip():
            raise CourseServiceError("Module title is required.")
        try:
            return CourseDAO.add_module(course_id, title.strip(), order_index)
        except DAOError as exc:
            raise CourseServiceError(str(exc)) from exc

    @staticmethod
    def get_module(module_id: int):
        try:
            module = CourseDAO.get_module(module_id)
        except DAOError as exc:
            raise CourseServiceError(str(exc)) from exc
        if not module:
            raise CourseServiceError("Module not found.")
        return module

    @staticmethod
    def list_modules(course_id: int):
        try:
            return CourseDAO.get_modules_for_course(course_id)
        except DAOError as exc:
            raise CourseServiceError(str(exc)) from exc

    # ── Lessons ───────────────────────────────────────────────────────
    @staticmethod
    def add_lesson(module_id: int, title: str, content: str, order_index: int = 0):
        CourseService.get_module(module_id)          # ensures module exists
        if not title or not title.strip():
            raise CourseServiceError("Lesson title is required.")
        try:
            return CourseDAO.add_lesson(module_id, title.strip(), content, order_index)
        except DAOError as exc:
            raise CourseServiceError(str(exc)) from exc

    @staticmethod
    def get_lesson(lesson_id: int):
        try:
            lesson = CourseDAO.get_lesson(lesson_id)
        except DAOError as exc:
            raise CourseServiceError(str(exc)) from exc
        if not lesson:
            raise CourseServiceError("Lesson not found.")
        return lesson

    @staticmethod
    def list_lessons(module_id: int):
        try:
            return CourseDAO.get_lessons_for_module(module_id)
        except DAOError as exc:
            raise CourseServiceError(str(exc)) from exc

    # ── Enrollment ────────────────────────────────────────────────────
    @staticmethod
    def enroll_student(student_id: int, course_id: int):
        CourseService.get_course(course_id)          # ensures course exists
        try:
            existing = EnrollmentDAO.get_by_student_and_course(student_id, course_id)
        except DAOError as exc:
            raise CourseServiceError(str(exc)) from exc
        if existing:
            raise CourseServiceError("Already enrolled in this course.")
        try:
            return EnrollmentDAO.create(student_id, course_id)
        except DAOError as exc:
            raise CourseServiceError(str(exc)) from exc

    @staticmethod
    def list_enrollments_for_student(student_id: int):
        try:
            return EnrollmentDAO.get_for_student(student_id)
        except DAOError as exc:
            raise CourseServiceError(str(exc)) from exc

    @staticmethod
    def list_enrollments_for_course(course_id: int):
        try:
            return EnrollmentDAO.get_for_course(course_id)
        except DAOError as exc:
            raise CourseServiceError(str(exc)) from exc
