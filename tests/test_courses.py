from tests.conftest import register_user, login_user
from services.course_service import CourseService
from dao.user_dao import UserDAO


def _make_instructor(client):
    register_user(client, "Instructor One", "instr1@example.com", "password123", "instructor")
    login_user(client, "instr1@example.com", "password123")
    return UserDAO.get_by_email("instr1@example.com")


def test_instructor_can_create_course(client, app):
    instructor = _make_instructor(client)
    resp = client.post(
        "/instructor/courses/create",
        data={"title": "Python 101", "description": "Intro to Python"},
        follow_redirects=True,
    )
    assert b"Course created" in resp.data
    with app.app_context():
        courses = CourseService.list_courses_for_instructor(instructor.id)
        assert len(courses) == 1
        assert courses[0].title == "Python 101"


def test_student_cannot_create_course(client):
    register_user(client, "Student One", "stud1@example.com", "password123", "student")
    login_user(client, "stud1@example.com", "password123")
    resp = client.post(
        "/instructor/courses/create", data={"title": "Hack", "description": "x"}, follow_redirects=True
    )
    assert b"do not have permission" in resp.data


def test_add_module_and_lesson(client, app):
    _make_instructor(client)
    client.post("/instructor/courses/create", data={"title": "Course A", "description": "d"}, follow_redirects=True)
    with app.app_context():
        course = CourseService.list_courses()[0]
        course_id = course.id

    client.post(f"/instructor/courses/{course_id}/modules/create", data={"title": "Module 1"}, follow_redirects=True)
    with app.app_context():
        modules = CourseService.list_modules(course_id)
        assert len(modules) == 1
        module_id = modules[0].id

    resp = client.post(
        f"/instructor/modules/{module_id}/lessons/create",
        data={"title": "Lesson 1", "content": "Some content"},
        follow_redirects=True,
    )
    assert b"Lesson added" in resp.data
    with app.app_context():
        lessons = CourseService.list_lessons(module_id)
        assert len(lessons) == 1


def test_student_can_enroll_in_course(client, app):
    _make_instructor(client)
    client.post("/instructor/courses/create", data={"title": "Course B", "description": "d"}, follow_redirects=True)
    client.get("/logout")

    register_user(client, "Student Two", "stud2@example.com", "password123", "student")
    login_user(client, "stud2@example.com", "password123")

    with app.app_context():
        course_id = CourseService.list_courses()[0].id

    resp = client.post(f"/student/courses/{course_id}/enroll", follow_redirects=True)
    assert b"Enrolled successfully" in resp.data


def test_cannot_enroll_twice(client, app):
    _make_instructor(client)
    client.post("/instructor/courses/create", data={"title": "Course C", "description": "d"}, follow_redirects=True)
    client.get("/logout")

    register_user(client, "Student Three", "stud3@example.com", "password123", "student")
    login_user(client, "stud3@example.com", "password123")

    with app.app_context():
        course_id = CourseService.list_courses()[0].id

    client.post(f"/student/courses/{course_id}/enroll", follow_redirects=True)
    resp = client.post(f"/student/courses/{course_id}/enroll", follow_redirects=True)
    assert b"Already enrolled" in resp.data
