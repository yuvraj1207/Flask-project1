from tests.conftest import register_user, login_user
from services.course_service import CourseService
from services.quiz_service import QuizService


def _setup_course_module(client):
    register_user(client, "Instructor Q", "instrq@example.com", "password123", "instructor")
    login_user(client, "instrq@example.com", "password123")
    client.post("/instructor/courses/create", data={"title": "Quiz Course", "description": "d"}, follow_redirects=True)
    course_id = CourseService.list_courses()[0].id
    client.post(f"/instructor/courses/{course_id}/modules/create", data={"title": "Module Q"}, follow_redirects=True)
    module_id = CourseService.list_modules(course_id)[0].id
    return course_id, module_id


def test_create_quiz_and_add_questions(client, app):
    with app.app_context():
        course_id, module_id = _setup_course_module(client)
        client.post(
            f"/instructor/modules/{module_id}/quizzes/create",
            data={"title": "Quiz 1", "pass_percent": "50"},
            follow_redirects=True,
        )
        quiz_id = QuizService.list_quizzes(module_id)[0].id

        resp = client.post(
            f"/instructor/quizzes/{quiz_id}/questions/create",
            data={
                "text": "2 + 2 = ?",
                "option_a": "3",
                "option_b": "4",
                "option_c": "5",
                "option_d": "6",
                "correct_option": "b",
                "points": "1",
            },
            follow_redirects=True,
        )
        assert b"Question added" in resp.data
        assert len(QuizService.get_questions(quiz_id)) == 1


def test_quiz_scoring_calculation(client, app):
    with app.app_context():
        course_id, module_id = _setup_course_module(client)
        client.post(
            f"/instructor/modules/{module_id}/quizzes/create",
            data={"title": "Scored Quiz", "pass_percent": "50"},
            follow_redirects=True,
        )
        quiz_id = QuizService.list_quizzes(module_id)[0].id

        q1 = QuizService.add_question(quiz_id, "Q1", "a", "b", "c", "d", "a", points=1)
        q2 = QuizService.add_question(quiz_id, "Q2", "a", "b", "c", "d", "c", points=1)

        client.get("/logout")
        register_user(client, "Quiz Student", "quizstud@example.com", "password123", "student")
        login_user(client, "quizstud@example.com", "password123")
        client.post(f"/student/courses/{course_id}/enroll", follow_redirects=True)

        resp = client.post(
            f"/quizzes/{quiz_id}/submit",
            data={f"question_{q1.id}": "a", f"question_{q2.id}": "d"},
            follow_redirects=True,
        )
        assert b"scored" in resp.data
        results = QuizService.get_results_for_quiz(quiz_id)
        assert len(results) == 1
        assert results[0].score == 1
        assert results[0].total == 2
        assert results[0].percent == 50.0
        assert results[0].passed is True


def test_quiz_with_no_questions_raises_error(client, app):
    with app.app_context():
        course_id, module_id = _setup_course_module(client)
        client.post(
            f"/instructor/modules/{module_id}/quizzes/create",
            data={"title": "Empty Quiz", "pass_percent": "50"},
            follow_redirects=True,
        )
        quiz_id = QuizService.list_quizzes(module_id)[0].id

        client.get("/logout")
        register_user(client, "Empty Student", "emptystud@example.com", "password123", "student")
        login_user(client, "emptystud@example.com", "password123")

        resp = client.post(f"/quizzes/{quiz_id}/submit", data={}, follow_redirects=True)
        assert b"no questions yet" in resp.data
