import os
import time
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for
from config.database import db, init_db
from utils.logger import setup_logging
from utils.template_filter import register_filters
from sqlalchemy import create_engine, text

load_dotenv()


def create_app(database_uri: str = None) -> Flask:
    app = Flask(__name__)

    # ── Flask Secret Key Configuration ───────────────────────────────────────
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-prod")

    # ── Database URI Configuration ───────────────────────────────────────────
    db_uri = (
        database_uri
        or os.environ.get("SQLALCHEMY_DATABASE_URI")
        or os.environ.get("MYSQL_DB_URL")
        or os.environ.get("DATABASE_URI")
        or os.environ.get("DATABASE_URL")
        or "mysql+pymysql://root:yuvraj@localhost:3306/lms_db"
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri

    # ── Core configuration ────────────────────────────────────────────────────
    init_db(app)

    # ── File upload configuration ─────────────────────────────────────────────
    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

    app.config["ALLOWED_EXTENSIONS"] = {
        "pdf":   {"pdf"},
        "image": {"jpg", "jpeg", "png", "gif", "webp"},
        "video": {"mp4", "avi", "mov", "mkv", "webm"},
        "doc":   {"doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt"},
    }

    app.config["MAX_FILE_SIZE"] = {
        "pdf":   20 * 1024 * 1024,
        "image":  5 * 1024 * 1024,
        "video": 100 * 1024 * 1024,
        "doc":   10 * 1024 * 1024,
    }

    # ── Logging configuration ─────────────────────────────────────────────────
    app.config["LOG_FOLDER"] = os.path.join(app.instance_path, "logs")
    os.makedirs(app.config["LOG_FOLDER"], exist_ok=True)
    setup_logging(app)

    # ── Register template filters ─────────────────────────────────────────────
    register_filters(app)

    # ── Routes ────────────────────────────────────────────────────────────────
    @app.route("/")
    def index():
        return redirect(url_for("auth.login"))

    @app.route('/health', methods=['GET', 'HEAD'])
    @app.route('/health/', methods=['GET', 'HEAD'])
    def health():
        return {'status': 'healthy'}, 200

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

    # ── Database initialization with retry logic & timeouts ───────────────────
    with app.app_context():
        import models  # noqa: F401

        retries = 5
        while retries > 0:
            try:
                db_url = app.config["SQLALCHEMY_DATABASE_URI"]
                if "mysql" in db_url and "/" in db_url:
                    base_uri, db_name = db_url.rsplit("/", 1)
                    if "?" in db_name:
                        db_name = db_name.split("?")[0]
                    if db_name:
                        engine = create_engine(base_uri, connect_args={"connect_timeout": 5})
                        with engine.connect() as conn:
                            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{db_name}`"))
                            conn.commit()

                db.create_all()
                print("✅ Connected to MySQL successfully!", flush=True)
                break
            except Exception as e:
                retries -= 1
                print(f"❌ MySQL not ready, retrying... ({retries} attempts left): {e}", flush=True)
                time.sleep(3)
                if retries == 0:
                    print("⚠️ Starting app without immediate DB connection — will retry on request.", flush=True)

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    debug = os.environ.get("APP_ENV", "development") != "production"
    app.run(host="0.0.0.0", port=port, debug=debug)