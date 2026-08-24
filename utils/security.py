from functools import wraps
from flask import session, jsonify, redirect, url_for, flash, request


def _current_role() -> str:
    return session.get("role", "")


def _unauthorized(message: str = "You do not have permission to access this page."):
    """Return 403 JSON for API routes, or flash+redirect for web routes."""
    if request.path.startswith("/api"):
        return jsonify({"error": message}), 403
    flash(message, "danger")
    return redirect(url_for("auth.login"))


def login_required(f):
    """Decorator: ensures any authenticated user is logged in."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            if request.path.startswith("/api"):
                return jsonify({"error": "Authentication required."}), 401
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return wrapper


def role_required(*roles):
    """Decorator factory: restricts access to specified roles."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                if request.path.startswith("/api"):
                    return jsonify({"error": "Authentication required."}), 401
                flash("Please log in to continue.", "warning")
                return redirect(url_for("auth.login"))
            if _current_role() not in roles:
                return _unauthorized("You do not have permission to access this page.")
            return f(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(f):
    return role_required("admin")(f)


def instructor_required(f):
    return role_required("instructor", "admin")(f)


def student_required(f):
    return role_required("student", "admin")(f)
