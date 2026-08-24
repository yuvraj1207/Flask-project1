from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.security import instructor_required
from services.course_service import CourseService, CourseServiceError
from services.quiz_service import QuizService, QuizServiceError
from services.file_service import FileService, FileServiceError
from dao.user_dao import UserDAO, DAOError

instructor_bp = Blueprint("instructor", __name__, url_prefix="/instructor")


@instructor_bp.route("/dashboard")
@instructor_required
def dashboard():
    try:
        courses = CourseService.list_courses_for_instructor(session["user_id"])
    except CourseServiceError as exc:
        flash(str(exc), "danger")
        courses = []
    return render_template("instructor_dashboard.html", courses=courses)


@instructor_bp.route("/courses/create", methods=["GET", "POST"])
@instructor_required
def create_course():
    if request.method == "POST":
        try:
            CourseService.create_course(
                title=request.form.get("title", "").strip(),
                description=request.form.get("description", ""),
                instructor_id=session["user_id"],
            )
            flash("Course created.", "success")
            return redirect(url_for("instructor.dashboard"))
        except CourseServiceError as exc:
            flash(str(exc), "danger")
    return render_template("course_detail.html", course=None, modules=[])


@instructor_bp.route("/courses/<int:course_id>/modules/create", methods=["POST"])
@instructor_required
def create_module(course_id):
    try:
        CourseService.add_module(course_id, request.form.get("title", "").strip())
        flash("Module added.", "success")
    except CourseServiceError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("course.course_detail", course_id=course_id))


@instructor_bp.route("/modules/<int:module_id>/lessons/create", methods=["POST"])
@instructor_required
def create_lesson(module_id):
    try:
        module = CourseService.get_module(module_id)
        CourseService.add_lesson(
            module_id,
            title=request.form.get("title", "").strip(),
            content=request.form.get("content", ""),
        )
        flash("Lesson added.", "success")
        return redirect(url_for("course.course_detail", course_id=module.course_id))
    except CourseServiceError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("instructor.dashboard"))


@instructor_bp.route("/modules/<int:module_id>/quizzes/create", methods=["POST"])
@instructor_required
def create_quiz(module_id):
    try:
        module = CourseService.get_module(module_id)
        pass_pct = float(request.form.get("pass_percent", 50))
        QuizService.create_quiz(module_id, request.form.get("title", "").strip(), pass_pct)
        flash("Quiz created.", "success")
        return redirect(url_for("course.course_detail", course_id=module.course_id))
    except (CourseServiceError, QuizServiceError, ValueError) as exc:
        flash(str(exc), "danger")
        return redirect(url_for("instructor.dashboard"))


@instructor_bp.route("/quizzes/<int:quiz_id>/questions/create", methods=["POST"])
@instructor_required
def add_question(quiz_id):
    try:
        QuizService.add_question(
            quiz_id=quiz_id,
            text=request.form.get("text", "").strip(),
            option_a=request.form.get("option_a", ""),
            option_b=request.form.get("option_b", ""),
            option_c=request.form.get("option_c", ""),
            option_d=request.form.get("option_d", ""),
            correct_option=request.form.get("correct_option", ""),
            points=int(request.form.get("points", 1)),
        )
        flash("Question added.", "success")
        quiz   = QuizService.get_quiz(quiz_id)
        module = CourseService.get_module(quiz.module_id)
        return redirect(url_for("course.course_detail", course_id=module.course_id))
    except (QuizServiceError, CourseServiceError, ValueError) as exc:
        flash(str(exc), "danger")
        return redirect(url_for("instructor.dashboard"))


@instructor_bp.route(
    "/courses/<int:course_id>/modules/<int:module_id>/materials/upload",
    methods=["POST"],
)
@instructor_required
def upload_material(course_id, module_id):
    try:
        uploader     = UserDAO.get_by_id(session["user_id"])
        file_storage = request.files.get("file")
        FileService.upload_material(file_storage, course_id, module_id, uploader)
        flash("File uploaded.", "success")
    except (FileServiceError, DAOError) as exc:
        flash(str(exc), "danger")
    return redirect(url_for("course.course_detail", course_id=course_id))


@instructor_bp.route("/courses/<int:course_id>/delete", methods=["POST"])
@instructor_required
def delete_course(course_id):
    try:
        course = CourseService.get_course(course_id)
        if course.instructor_id != session["user_id"] and session.get("role") != "admin":
            flash("You may only delete your own courses.", "danger")
            return redirect(url_for("instructor.dashboard"))
        CourseService.delete_course(course_id)
        flash("Course removed.", "success")
    except CourseServiceError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("instructor.dashboard"))
