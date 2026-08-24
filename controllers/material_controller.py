from flask import Blueprint, send_from_directory, current_app, redirect, url_for, flash, session
from utils.security import login_required, instructor_required
from services.file_service import FileService, FileServiceError
from dao.user_dao import UserDAO, DAOError

material_bp = Blueprint("material", __name__, url_prefix="/materials")


@material_bp.route("/<int:material_id>/download")
@login_required
def download(material_id):
    try:
        material = FileService.get_material(material_id)
    except FileServiceError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("course.course_list"))
    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        material.stored_path,
        as_attachment=True,
        download_name=material.filename,
    )


@material_bp.route("/<int:material_id>/delete", methods=["POST"])
@instructor_required
def delete(material_id):
    try:
        requester = UserDAO.get_by_id(session["user_id"])
        course_id = FileService.get_material(material_id).course_id
        FileService.delete_material(material_id, requester)
        flash("Material deleted.", "success")
        return redirect(url_for("course.course_detail", course_id=course_id))
    except (FileServiceError, DAOError) as exc:
        flash(str(exc), "danger")
        return redirect(url_for("instructor.dashboard"))
