from sqlalchemy.exc import SQLAlchemyError
from models import db
from models.course import Course, Module, Lesson
from dao.user_dao import DAOError


class CourseDAO:

    # ── Courses ──────────────────────────────────────────────────────
    @staticmethod
    def create_course(title: str, description: str, instructor_id: int) -> Course:
        try:
            course = Course(title=title, description=description, instructor_id=instructor_id)
            db.session.add(course)
            db.session.commit()
            return course
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise DAOError(f"Failed to create course: {exc}") from exc

    @staticmethod
    def get_course(course_id: int):
        try:
            return db.session.get(Course, course_id)
        except SQLAlchemyError as exc:
            raise DAOError(f"Failed to fetch course: {exc}") from exc

    @staticmethod
    def get_all_courses():
        try:
            return Course.query.order_by(Course.id.desc()).all()
        except SQLAlchemyError as exc:
            raise DAOError(f"Failed to list courses: {exc}") from exc

    @staticmethod
    def get_courses_by_instructor(instructor_id: int):
        try:
            return Course.query.filter_by(instructor_id=instructor_id).all()
        except SQLAlchemyError as exc:
            raise DAOError(f"Failed to list courses for instructor: {exc}") from exc

    @staticmethod
    def update_course(course: Course, **kwargs) -> Course:
        try:
            for key, value in kwargs.items():
                setattr(course, key, value)
            db.session.commit()
            return course
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise DAOError(f"Failed to update course: {exc}") from exc

    @staticmethod
    def delete_course(course: Course) -> None:
        try:
            db.session.delete(course)
            db.session.commit()
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise DAOError(f"Failed to delete course: {exc}") from exc

    # ── Modules ───────────────────────────────────────────────────────
    @staticmethod
    def add_module(course_id: int, title: str, order_index: int = 0) -> Module:
        try:
            module = Module(course_id=course_id, title=title, order_index=order_index)
            db.session.add(module)
            db.session.commit()
            return module
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise DAOError(f"Failed to add module: {exc}") from exc

    @staticmethod
    def get_module(module_id: int):
        try:
            return db.session.get(Module, module_id)
        except SQLAlchemyError as exc:
            raise DAOError(f"Failed to fetch module: {exc}") from exc

    @staticmethod
    def get_modules_for_course(course_id: int):
        try:
            return Module.query.filter_by(course_id=course_id).order_by(Module.order_index).all()
        except SQLAlchemyError as exc:
            raise DAOError(f"Failed to list modules: {exc}") from exc

    @staticmethod
    def delete_module(module: Module) -> None:
        try:
            db.session.delete(module)
            db.session.commit()
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise DAOError(f"Failed to delete module: {exc}") from exc

    # ── Lessons ───────────────────────────────────────────────────────
    @staticmethod
    def add_lesson(module_id: int, title: str, content: str, order_index: int = 0) -> Lesson:
        try:
            lesson = Lesson(module_id=module_id, title=title, content=content, order_index=order_index)
            db.session.add(lesson)
            db.session.commit()
            return lesson
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise DAOError(f"Failed to add lesson: {exc}") from exc

    @staticmethod
    def get_lesson(lesson_id: int):
        try:
            return db.session.get(Lesson, lesson_id)
        except SQLAlchemyError as exc:
            raise DAOError(f"Failed to fetch lesson: {exc}") from exc

    @staticmethod
    def get_lessons_for_module(module_id: int):
        try:
            return Lesson.query.filter_by(module_id=module_id).order_by(Lesson.order_index).all()
        except SQLAlchemyError as exc:
            raise DAOError(f"Failed to list lessons: {exc}") from exc

    @staticmethod
    def delete_lesson(lesson: Lesson) -> None:
        try:
            db.session.delete(lesson)
            db.session.commit()
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise DAOError(f"Failed to delete lesson: {exc}") from exc
