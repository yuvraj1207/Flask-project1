from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from services.auth_service import AuthService, AuthError
from utils.logger import audit_log

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name     = request.form.get("name", "").strip()
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        role     = request.form.get("role", "student")
        try:
            AuthService.register(name, email, password, role)

            audit_log(
                "REGISTRATION_SUCCESS | email=%s | role=%s",
                email,
                role
            )

            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("auth.login"))
        except AuthError as exc:

            audit_log(
                "REGISTRATION_FAILURE | email=%s | role=%s | reason=%s",
                email,
                role,
                str(exc)
            )

            flash(str(exc), "danger")
    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        try:
            user = AuthService.authenticate(email, password)

            audit_log(
                "LOGIN_SUCCESS | user_id=%s | email=%s | role=%s",    # Audit log: successful login      
                user.id,
                email,
                user.role
            )

            session["user_id"] = user.id
            session["role"]    = user.role
            session["name"]    = user.name
            flash(f"Welcome back, {user.name}!", "success")
            if user.role == "admin":
                return redirect(url_for("admin.dashboard"))
            if user.role == "instructor":
                return redirect(url_for("instructor.dashboard"))
            return redirect(url_for("student.dashboard"))
        except AuthError as exc:

            # Audit log: failed login
            audit_log(
                "LOGIN_FAILURE | email=%s | reason=%s",
                email,
                str(exc)
            )

            flash(str(exc), "danger")
    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    user_id = session.get("user_id")
    role = session.get("role")

    # Audit log: logout
    audit_log(
        "LOGOUT | user_id=%s | role=%s",
        user_id,
        role
    )

    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/api/auth/login", methods=["POST"])
def api_login():
    data = request.get_json(force=True, silent=True)
    if not isinstance(data, dict):
        data = request.form.to_dict() if request.form else {}
    try:
        user  = AuthService.authenticate(data.get("email", ""), data.get("password", ""))

        # Audit log: successful API login
        audit_log(
            "API_LOGIN_SUCCESS | user_id=%s | email=%s | role=%s",
            user.id,
            data.get("email", ""),
            user.role
        )

        token = AuthService.generate_jwt(user)
        return jsonify({"token": token, "user": user.to_dict()})
    except AuthError as exc:

        # Audit log: failed API login
        audit_log(
            "API_LOGIN_FAILURE | email=%s | reason=%s",
            data.get("email", ""),
            str(exc)
        )

        return jsonify({"error": str(exc)}), 401    #deserlisation