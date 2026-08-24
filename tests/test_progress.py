from tests.conftest import register_user, login_user
from services.course_service import CourseService
from services.progress_service import ProgressService, ProgressServiceError
import pytest


def _setup(client):
    register_user(client, "Instructor P", "instrp@example.com", "password123", "instructor")
    login_user(client, "instrp@example.com", "password123")
    client.post("/instructor/courses/create", data={"title": "Progress Course", "description": "d"}, follow_redirects=True)
    course_id = CourseService.list_courses()[0].id
    client.post(f"/instructor/courses/{course_id}/modules/create", data={"title": "M1"}, follow_redirects=True)
    module_id = CourseService.list_modules(course_id)[0].id
    client.post(f"/instructor/modules/{module_id}/lessons/create", data={"title": "L1", "content": "c"}, follow_redirects=True)
    client.post(f"/instructor/modules/{module_id}/lessons/create", data={"title": "L2", "content": "c"}, follow_redirects=True)
    lessons = CourseService.list_lessons(module_id)

    client.get("/logout")
    register_user(client, "Progress Student", "progstud@example.com", "password123", "student")
    login_user(client, "progstud@example.com", "password123")
    client.post(f"/student/courses/{course_id}/enroll", follow_redirects=True)
    return course_id, lessons


def test_progress_increases_as_lessons_completed(client, app):
    with app.app_context():
        course_id, lessons = _setup(client)

        resp = client.post(
            f"/student/courses/{course_id}/lessons/{lessons[0].id}/complete", follow_redirects=True
        )
        assert b"marked complete" in resp.data

        from dao.user_dao import UserDAO
        student = UserDAO.get_by_email("progstud@example.com")
        enrollment = ProgressService.get_progress(student.id, course_id)
        assert enrollment.progress_percent == 50.0

        client.post(f"/student/courses/{course_id}/lessons/{lessons[1].id}/complete", follow_redirects=True)
        enrollment = ProgressService.get_progress(student.id, course_id)
        assert enrollment.progress_percent == 100.0


def test_progress_requires_enrollment(app):
    with app.app_context():
        with pytest.raises(ProgressServiceError):
            ProgressService.get_progress(9999, 9999)


def test_learning_history_contains_enrollments_and_results(client, app):
    with app.app_context():
        course_id, lessons = _setup(client)
        from dao.user_dao import UserDAO
        student = UserDAO.get_by_email("progstud@example.com")
        history = ProgressService.get_learning_history(student.id)
        assert len(history["enrollments"]) == 1
        assert history["quiz_results"] == []
