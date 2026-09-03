import datetime
import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    app.config.setdefault(
        "SQLALCHEMY_DATABASE_URI",os.getenv("DATABASE_URL")
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["SECRET_KEY"] = (
        app.config.get("SECRET_KEY") or os.getenv("SECRET_KEY")
    )

    app.secret_key = app.config["SECRET_KEY"]

    app.config["JWT_SECRET_KEY"] = (
        app.config.get("JWT_SECRET_KEY") or os.getenv("JWT_SECRET_KEY")
    )

    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(hours=12)

    db.init_app(app)