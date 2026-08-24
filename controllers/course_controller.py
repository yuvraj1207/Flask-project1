from flask import Blueprint, render_template, flash, redirect, url_for, session
from utils.security import login_required
from services.course_service import CourseService, CourseServiceError
from services.quiz_service import QuizService
from services.file_service import FileService
from services.progress_service import ProgressService

course_bp = Blueprint("course", __name__, url_prefix="/courses")


@course_bp.route("/")
def course_list():
    try:
        courses = CourseService.list_courses()
    except CourseServiceError as exc:
        flash(str(exc), "danger")
        courses = []
    return render_template("course_list.html", courses=courses)


@course_bp.route("/<int:course_id>")
def course_detail(course_id):
    try:
        course  = CourseService.get_course(course_id)
        modules = CourseService.list_modules(course_id)
        modules_with_content = [
            {
                "module":    module,
                "lessons":   CourseService.list_lessons(module.id),
                "quizzes":   QuizService.list_quizzes(module.id),
                "materials": FileService.list_materials_for_module(module.id),
            }
            for module in modules
        ]
        is_enrolled = False
        progress_info = None
        if session.get("user_id") and session.get("role") == "student":
            try:
                progress_info = ProgressService.get_progress(session["user_id"], course_id)
                is_enrolled = True
            except Exception:
                is_enrolled = False
    except CourseServiceError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("course.course_list"))
    return render_template(
        "course_detail.html",
        course=course,
        modules=modules_with_content,
        is_enrolled=is_enrolled,
        progress_info=progress_info,
    )


@course_bp.route("/lessons/<int:lesson_id>")
@login_required
def lesson_detail(lesson_id):
    try:
        lesson = CourseService.get_lesson(lesson_id)
    except CourseServiceError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("course.course_list"))
    return render_template("lesson.html", lesson=lesson)
