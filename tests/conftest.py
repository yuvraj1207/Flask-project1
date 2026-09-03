import os
import sys

# Allow imports from the project root
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

import pytest

from config.database import db
from app import create_app


# ------------------------------------------------------------
# Test Database Configuration
# ------------------------------------------------------------

TEST_DATABASE_URI = os.environ.get(
    "TEST_DATABASE_URI",
    "mysql+pymysql://root:yuvraj@localhost/lms_test_db"
)


# ------------------------------------------------------------
# Application Fixture
# ------------------------------------------------------------

@pytest.fixture(scope="function")
def app():
    """
    Create a fresh Flask application and a clean MySQL
    database schema for every test.
    """

    application = create_app(
        database_uri=TEST_DATABASE_URI
    )

    with application.app_context():

        from sqlalchemy import text

        db.session.remove()

        try:
            # Disable foreign-key checks while rebuilding schema
            db.session.execute(
                text("SET FOREIGN_KEY_CHECKS = 0")
            )

            # Remove all existing tables
            db.drop_all()

            # Recreate all tables
            db.create_all()

            # Enable foreign-key checks again
            db.session.execute(
                text("SET FOREIGN_KEY_CHECKS = 1")
            )

            db.session.commit()

        except Exception:
            db.session.rollback()

            # Try to restore a clean schema
            try:
                db.session.execute(
                    text("SET FOREIGN_KEY_CHECKS = 0")
                )

                db.drop_all()
                db.create_all()

                db.session.execute(
                    text("SET FOREIGN_KEY_CHECKS = 1")
                )

                db.session.commit()

            except Exception:
                db.session.rollback()
                raise

        yield application

        # ----------------------------------------------------
        # Cleanup after test
        # ----------------------------------------------------

        db.session.remove()

        try:
            db.session.execute(
                text("SET FOREIGN_KEY_CHECKS = 0")
            )

            db.drop_all()

            db.session.execute(
                text("SET FOREIGN_KEY_CHECKS = 1")
            )

            db.session.commit()

        except Exception:
            db.session.rollback()

            try:
                db.session.execute(
                    text("SET FOREIGN_KEY_CHECKS = 0")
                )

                db.drop_all()

                db.session.execute(
                    text("SET FOREIGN_KEY_CHECKS = 1")
                )

                db.session.commit()

            except Exception:
                db.session.rollback()
                raise


# ------------------------------------------------------------
# Flask Test Client
# ------------------------------------------------------------

@pytest.fixture()
def client(app):
    return app.test_client()


# ------------------------------------------------------------
# Database Fixture
# ------------------------------------------------------------

@pytest.fixture()
def database(app):
    return db


# ------------------------------------------------------------
# Helper: Register User
# ------------------------------------------------------------

def register_user(
    client,
    name: str,
    email: str,
    password: str,
    role: str
):
    return client.post(
        "/register",
        data={
            "name": name,
            "email": email,
            "password": password,
            "role": role
        },
        follow_redirects=True
    )


# ------------------------------------------------------------
# Helper: Normal Login
# ------------------------------------------------------------

def login_user(
    client,
    email: str,
    password: str
):
    return client.post(
        "/login",
        data={
            "email": email,
            "password": password
        },
        follow_redirects=True
    )