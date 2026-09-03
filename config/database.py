import datetime
import os

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def init_db(app):
    """
    Initialize Flask-SQLAlchemy and application security settings.

    The database URI is configured by create_app() in app.py.
    This function does not override it.
    """

    # --------------------------------------------------------
    # SQLAlchemy
    # --------------------------------------------------------

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # --------------------------------------------------------
    # Flask Session Secret
    # --------------------------------------------------------

    app.config["SECRET_KEY"] = (
        app.config.get("SECRET_KEY")
        or os.getenv("SECRET_KEY")
        or "dev-secret-key-change-in-prod"
    )

    app.secret_key = app.config["SECRET_KEY"]

    # --------------------------------------------------------
    # JWT Configuration
    # --------------------------------------------------------

    app.config["JWT_SECRET_KEY"] = (
        app.config.get("JWT_SECRET_KEY")
        or os.getenv("JWT_SECRET_KEY")
        or "dev-jwt-secret-key-change-in-prod"
    )

    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = (
        datetime.timedelta(hours=12)
    )

    # --------------------------------------------------------
    # Initialize SQLAlchemy
    # --------------------------------------------------------

    db.init_app(app)