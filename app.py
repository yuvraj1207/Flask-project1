import os
import time

from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for
from sqlalchemy import create_engine, text

from config.database import db, init_db
from utils.logger import setup_logging
from utils.template_filter import register_filters


# Load variables from .env
load_dotenv()


def create_app(database_uri: str = None) -> Flask:
    """
    Flask application factory.

    database_uri:
        Optional database URI. Tests can pass their own database URI.
        Normal application execution uses DATABASE_URL.
    """

    app = Flask(__name__)

    # ========================================================
    # Database Configuration
    # ========================================================

    db_uri = (
        database_uri
        or os.environ.get("DATABASE_URL")
        or os.environ.get("SQLALCHEMY_DATABASE_URI")
        or os.environ.get("MYSQL_DB_URL")
        or os.environ.get("DATABASE_URI")
    )

    if not db_uri:
        raise RuntimeError(
            "Database URI is not configured. "
            "Pass database_uri to create_app() "
            "or set the DATABASE_URL environment variable."
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri

    # ========================================================
    # Flask Secret Key
    # ========================================================

    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY",
        "dev-secret-key-change-in-prod"
    )

    # ========================================================
    # Initialize Database
    # ========================================================

    init_db(app)

    # ========================================================
    # File Upload Configuration
    # ========================================================

    app.config["UPLOAD_FOLDER"] = os.path.join(
        app.root_path,
        "static",
        "uploads"
    )

    os.makedirs(
        app.config["UPLOAD_FOLDER"],
        exist_ok=True
    )

    app.config["MAX_CONTENT_LENGTH"] = (
        50 * 1024 * 1024
    )

    app.config["ALLOWED_EXTENSIONS"] = {
        "pdf": {
            "pdf"
        },
        "image": {
            "jpg",
            "jpeg",
            "png",
            "gif",
            "webp"
        },
        "video": {
            "mp4",
            "avi",
            "mov",
            "mkv",
            "webm"
        },
        "doc": {
            "doc",
            "docx",
            "xls",
            "xlsx",
            "ppt",
            "pptx",
            "txt"
        }
    }

    app.config["MAX_FILE_SIZE"] = {
        "pdf": 20 * 1024 * 1024,
        "image": 5 * 1024 * 1024,
        "video": 100 * 1024 * 1024,
        "doc": 10 * 1024 * 1024
    }

    # ========================================================
    # Logging Configuration
    # ========================================================

    app.config["LOG_FOLDER"] = os.path.join(
        app.instance_path,
        "logs"
    )

    os.makedirs(
        app.config["LOG_FOLDER"],
        exist_ok=True
    )

    setup_logging(app)

    # ========================================================
    # Template Filters
    # ========================================================

    register_filters(app)

    # ========================================================
    # Basic Routes
    # ========================================================

    @app.route("/")
    def index():
        return redirect(
            url_for("auth.login")
        )

    @app.route(
        "/health",
        methods=["GET", "HEAD"]
    )
    @app.route(
        "/health/",
        methods=["GET", "HEAD"]
    )
    def health():
        return {
            "status": "healthy"
        }, 200

    # ========================================================
    # Register Blueprints
    # ========================================================

    from controllers.auth_controller import auth_bp
    from controllers.admin_controller import admin_bp
    from controllers.instructor_controller import instructor_bp
    from controllers.student_controller import student_bp
    from controllers.course_controller import course_bp
    from controllers.quiz_controller import quiz_bp
    from controllers.material_controller import material_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(instructor_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(material_bp)

    # ========================================================
    # Error Handlers
    # ========================================================

    @app.errorhandler(404)
    def not_found(error):
        return render_template(
            "base.html",
            error_message="Page not found (404)."
        ), 404

    @app.errorhandler(403)
    def forbidden(error):
        return render_template(
            "base.html",
            error_message="Forbidden (403)."
        ), 403

    @app.errorhandler(500)
    def server_error(error):
        return render_template(
            "base.html",
            error_message="Internal server error (500)."
        ), 500

    # ========================================================
    # Database Initialization
    # ========================================================

    with app.app_context():

        # Import all models so SQLAlchemy knows about them
        import models  # noqa: F401

        retries = 5

        while retries > 0:

            try:

                db_url = app.config[
                    "SQLALCHEMY_DATABASE_URI"
                ]

                # ------------------------------------------------
                # Create MySQL database if it does not exist
                # ------------------------------------------------

                if (
                    db_url
                    and "mysql" in db_url.lower()
                    and "/" in db_url
                ):

                    base_uri, db_name = db_url.rsplit(
                        "/",
                        1
                    )

                    # Remove query parameters
                    if "?" in db_name:
                        db_name = db_name.split(
                            "?",
                            1
                        )[0]

                    if db_name:

                        engine = create_engine(
                            base_uri,
                            connect_args={
                                "connect_timeout": 5
                            }
                        )

                        with engine.connect() as conn:

                            conn.execute(
                                text(
                                    f"CREATE DATABASE IF NOT EXISTS "
                                    f"`{db_name}`"
                                )
                            )

                            conn.commit()

                        engine.dispose()

                # ------------------------------------------------
                # Create tables
                # ------------------------------------------------

                db.create_all()

                print(
                    "✅ Connected to MySQL successfully!",
                    flush=True
                )

                break

            except Exception as e:

                retries -= 1

                print(
                    f"❌ MySQL not ready, retrying... "
                    f"({retries} attempts left): {e}",
                    flush=True
                )

                if retries > 0:
                    time.sleep(3)

                if retries == 0:

                    print(
                        "⚠️ Starting app without immediate "
                        "DB connection — will retry on request.",
                        flush=True
                    )

    return app


# ============================================================
# IMPORTANT:
#
# DO NOT write:
#
#     app = create_app()
#
# here.
#
# pytest imports create_app() from this module.
# Creating the application automatically during import
# prevents the test fixture from supplying TEST_DATABASE_URI.
# ============================================================


# ============================================================
# Application Entry Point
# ============================================================

if __name__ == "__main__":

    app = create_app()

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    debug = (
        os.environ.get(
            "APP_ENV",
            "development"
        )
        != "production"
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug
    )

