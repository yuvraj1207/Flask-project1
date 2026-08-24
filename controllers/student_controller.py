from flask import Blueprint, render_template, redirect, url_for, flash, session
from utils.security import student_required
from services.course_service import CourseService, CourseServiceError
from services.progress_service import ProgressService, ProgressServiceError

student_bp = Blueprint("student", __name__, url_prefix="/student")


@student_bp.route("/dashboard")
@student_required
def dashboard():
    try:
        enrollments = CourseService.list_enrollments_for_student(session["user_id"])
        courses     = CourseService.list_courses()
        enrolled_course_ids = {e.course_id for e in enrollments}
    except CourseServiceError as exc:
        flash(str(exc), "danger")
        enrollments, courses, enrolled_course_ids = [], [], set()
    return render_template(
        "student_dashboard.html",
        enrollments=enrollments,
        courses=courses,
        enrolled_course_ids=enrolled_course_ids,
    )


@student_bp.route("/courses/<int:course_id>/enroll", methods=["POST"])
@student_required
def enroll(course_id):
    try:
        CourseService.enroll_student(session["user_id"], course_id)
        flash("Enrolled successfully.", "success")
    except CourseServiceError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("student.dashboard"))


@student_bp.route("/progress")
@student_required
def progress():
    try:
        history = ProgressService.get_learning_history(session["user_id"])
    except ProgressServiceError as exc:
        flash(str(exc), "danger")
        history = {"enrollments": [], "quiz_results": []}
    return render_template("progress.html", **history)


@student_bp.route("/courses/<int:course_id>/lessons/<int:lesson_id>/complete", methods=["POST"])
@student_required
def complete_lesson(course_id, lesson_id):
    try:
        ProgressService.mark_lesson_complete(session["user_id"], course_id, lesson_id)
        flash("Lesson marked complete.", "success")
    except ProgressServiceError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("course.lesson_detail", lesson_id=lesson_id))
