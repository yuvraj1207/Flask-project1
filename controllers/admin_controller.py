from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from utils.security import admin_required
from utils.logger import audit_log
from dao.user_dao import UserDAO, DAOError
from services.course_service import CourseService, CourseServiceError
import os

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    try:
        users   = UserDAO.get_all()
        courses = CourseService.list_courses()

        audit_log(
            "ADMIN_DASHBOARD_ACCESS"
        )

    except (DAOError, CourseServiceError) as exc:
        flash(str(exc), "danger")
        users, courses = [], []

    # Read audit log for admin dashboard
    log_file = os.path.join(current_app.config["LOG_FOLDER"], "audit.log")
    try:
        with open(log_file, "r", encoding="utf-8") as file:
            logs = file.readlines()
    except (FileNotFoundError, OSError):
        logs = []

    return render_template(
        "admin_dashboard.html",
        users=users,
        courses=courses,
        logs=logs
    )


@admin_bp.route("/users")
@admin_required
def list_users():
    try:
        users   = UserDAO.get_all()
        courses = CourseService.list_courses()

        audit_log(
            "ADMIN_USER_LIST_VIEW"
        )

    except (DAOError, CourseServiceError) as exc:
        flash(str(exc), "danger")
        users, courses = [], []

    # Read audit log for admin dashboard
    log_file = os.path.join(current_app.config["LOG_FOLDER"], "audit.log")
    try:
        with open(log_file, "r", encoding="utf-8") as file:
            logs = file.readlines()
    except (FileNotFoundError, OSError):
        logs = []

    return render_template(
        "admin_dashboard.html",
        users=users,
        courses=courses,
        logs=logs
    )


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def delete_user(user_id):
    try:
        user = UserDAO.get_by_id(user_id)
        if user:
            UserDAO.delete(user)

            audit_log(
                "ADMIN_DELETE_USER | deleted_user_id=%s",
                user_id
            )

            flash("User removed.", "success")
        else:
            flash("User not found.", "warning")
    except DAOError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/courses/<int:course_id>/delete", methods=["POST"])
@admin_required
def delete_course(course_id):
    try:
        CourseService.delete_course(course_id)

        audit_log(
            "ADMIN_DELETE_COURSE | course_id=%s",
            course_id
        )

        flash("Course removed.", "success")
    except CourseServiceError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("admin.dashboard"))