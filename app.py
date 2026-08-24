import os
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for
from config.database import db, init_db
from utils.logger import setup_logging  # <-- 1. Import your logging setup

load_dotenv()


def create_app(database_uri: str = None) -> Flask:
    """Application factory.

    Args:
        database_uri: Override the default MySQL URI (used by tests).
    """
    app = Flask(__name__)

    # ── Override DB URI before init_db so it wins the setdefault ────────────
    if database_uri:
        app.config["SQLALCHEMY_DATABASE_URI"] = database_uri

    # ── Core configuration ────────────────────────────────────────────────────
    init_db(app)   # sets JWT config + calls db.init_app(app)

    # ── File upload configuration ─────────────────────────────────────────────
    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024   # 50 MB hard limit (Flask)

    # file_type → set of allowed extensions
    app.config["ALLOWED_EXTENSIONS"] = {
        "pdf":   {"pdf"},
        "image": {"jpg", "jpeg", "png", "gif", "webp"},
        "video": {"mp4", "avi", "mov", "mkv", "webm"},
        "doc":   {"doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt"},
    }

    # Per-type max byte sizes  (images: 5 MB  so the test at 6 MB fails)
    app.config["MAX_FILE_SIZE"] = {
        "pdf":   20 * 1024 * 1024,
        "image":  5 * 1024 * 1024,
        "video": 100 * 1024 * 1024,
        "doc":   10 * 1024 * 1024,
    }

    # ── Logging configuration ─────────────────────────────────────────────────
    app.config["LOG_FOLDER"] = os.path.join(app.instance_path, "logs")
    os.makedirs(app.config["LOG_FOLDER"], exist_ok=True)
    setup_logging(app)  # <-- 2. Initialize your custom logging

    # ── Register blueprints ───────────────────────────────────────────────────
    from controllers.auth_controller       import auth_bp
    from controllers.admin_controller      import admin_bp
    from controllers.instructor_controller import instructor_bp
    from controllers.student_controller    import student_bp
    from controllers.course_controller     import course_bp
    from controllers.quiz_controller       import quiz_bp
    from controllers.material_controller   import material_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(instructor_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(material_bp)

    # ── Routes ────────────────────────────────────────────────────────────────
    @app.route("/")
    def index():
        return redirect(url_for("auth.login"))

    # ── Error handlers ────────────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(error):
        return render_template("base.html", error_message="Page not found (404)."), 404

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("base.html", error_message="Forbidden (403)."), 403

    @app.errorhandler(500)
    def server_error(error):
        return render_template("base.html", error_message="Internal server error (500)."), 500

    # ── Create tables ─────────────────────────────────────────────────────────
    with app.app_context():
        # Import models here so their metadata is known before create_all
        import models  # noqa: F401
        db.create_all()

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)