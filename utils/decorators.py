from functools import wraps
from flask import session, redirect, url_for, flash, request, jsonify

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({"error": "Unauthorized access"}), 401
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                if request.is_json:
                    return jsonify({"error": "Unauthorized access"}), 401
                flash("Please log in to continue.", "warning")
                return redirect(url_for('auth.login'))
            
            user_role = session.get('role')
            if user_role not in allowed_roles:
                if request.is_json:
                    return jsonify({"error": "Forbidden access"}), 403
                flash("You do not have permission to access this resource.", "danger")
                return redirect(url_for('main.home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator