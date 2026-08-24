import io
from tests.conftest import register_user, login_user
from services.course_service import CourseService


def _setup(client):
    register_user(client, "Instructor F", "instrf@example.com", "password123", "instructor")
    login_user(client, "instrf@example.com", "password123")
    client.post("/instructor/courses/create", data={"title": "File Course", "description": "d"}, follow_redirects=True)
    course_id = CourseService.list_courses()[0].id
    client.post(f"/instructor/courses/{course_id}/modules/create", data={"title": "M1"}, follow_redirects=True)
    module_id = CourseService.list_modules(course_id)[0].id
    return course_id, module_id


def test_upload_allowed_pdf(client, app):
    with app.app_context():
        course_id, module_id = _setup(client)
        data = {"file": (io.BytesIO(b"%PDF-1.4 fake pdf content"), "notes.pdf")}
        resp = client.post(
            f"/instructor/courses/{course_id}/modules/{module_id}/materials/upload",
            data=data,
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        assert b"File uploaded" in resp.data


def test_upload_rejects_disallowed_extension(client, app):
    with app.app_context():
        course_id, module_id = _setup(client)
        data = {"file": (io.BytesIO(b"echo hi"), "script.exe")}
        resp = client.post(
            f"/instructor/courses/{course_id}/modules/{module_id}/materials/upload",
            data=data,
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        assert b"not allowed" in resp.data


def test_upload_rejects_oversized_image(client, app):
    with app.app_context():
        course_id, module_id = _setup(client)
        oversized = io.BytesIO(b"0" * (6 * 1024 * 1024))  # over the 5MB image cap
        data = {"file": (oversized, "big_photo.png")}
        resp = client.post(
            f"/instructor/courses/{course_id}/modules/{module_id}/materials/upload",
            data=data,
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        assert b"too large" in resp.data


def test_student_cannot_upload_material(client, app):
    with app.app_context():
        course_id, module_id = _setup(client)
        client.get("/logout")
        register_user(client, "File Student", "filestud@example.com", "password123", "student")
        login_user(client, "filestud@example.com", "password123")
        data = {"file": (io.BytesIO(b"content"), "notes.pdf")}
        resp = client.post(
            f"/instructor/courses/{course_id}/modules/{module_id}/materials/upload",
            data=data,
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        assert b"do not have permission" in resp.data
