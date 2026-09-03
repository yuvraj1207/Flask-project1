import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from config.database import db
from app import create_app

TEST_DATABASE_URI = "mysql+pymysql://root:yuvraj@localhost/lms_test_db"


@pytest.fixture(scope="function")
def app():
    """Create a fresh application and empty MySQL test database for each test."""
    application = create_app(database_uri=TEST_DATABASE_URI)

    with application.app_context():
        db.drop_all()    # clean slate
        db.create_all()  # rebuild schema

        yield application

        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def database(app):
    return db

def register_user(client, name: str, email: str, password: str, role: str):
    return client.post(
        "/register",
        data={"name": name, "email": email, "password": password, "role": role},
        follow_redirects=True,
    )


def login_user(client, email: str, password: str):
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )
