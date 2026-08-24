from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.security import student_required
from services.quiz_service import QuizService, QuizServiceError

quiz_bp = Blueprint("quiz", __name__, url_prefix="/quizzes")


@quiz_bp.route("/<int:quiz_id>")
@student_required
def take_quiz(quiz_id):
    try:
        quiz      = QuizService.get_quiz(quiz_id)
        questions = QuizService.get_questions(quiz_id)
    except QuizServiceError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("student.dashboard"))
    return render_template("quiz.html", quiz=quiz, questions=questions)


@quiz_bp.route("/<int:quiz_id>/submit", methods=["POST"])
@student_required
def submit_quiz(quiz_id):
    # Collect answers: form keys look like "question_<id>"
    answers = {}
    for key, value in request.form.items():
        if key.startswith("question_"):
            question_id       = key.replace("question_", "")
            answers[question_id] = value

    try:
        result = QuizService.evaluate_attempt(quiz_id, session["user_id"], answers)
        status = "Passed" if result.passed else "Failed"
        flash(f"You scored {result.percent}% — {status}.", "info")
    except QuizServiceError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("student.progress"))
