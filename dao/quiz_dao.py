from sqlalchemy.exc import SQLAlchemyError
from models import db
from models.quiz import Quiz, Question, QuizResult
from dao.user_dao import DAOError


class QuizDAO:

    # ── Quizzes ───────────────────────────────────────────────────────
    @staticmethod
    def create_quiz(module_id: int, title: str, pass_percent: float = 50.0) -> Quiz:
        try:
            quiz = Quiz(module_id=module_id, title=title, pass_percent=pass_percent)
            db.session.add(quiz)
            db.session.commit()
            return quiz
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise DAOError(f"Failed to create quiz: {exc}") from exc

    @staticmethod
    def get_quiz(quiz_id: int):
        try:
            return db.session.get(Quiz, quiz_id)
        except SQLAlchemyError as exc:
            raise DAOError(f"Failed to fetch quiz: {exc}") from exc

    @staticmethod
    def get_quizzes_for_module(module_id: int):
        try:
            return Quiz.query.filter_by(module_id=module_id).all()
        except SQLAlchemyError as exc:
            raise DAOError(f"Failed to list quizzes: {exc}") from exc

    @staticmethod
    def delete_quiz(quiz: Quiz) -> None:
        try:
            db.session.delete(quiz)
            db.session.commit()
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise DAOError(f"Failed to delete quiz: {exc}") from exc

    # ── Questions ─────────────────────────────────────────────────────
    @staticmethod
    def add_question(
        quiz_id: int,
        text: str,
        option_a: str,
        option_b: str,
        option_c: str,
        option_d: str,
        correct_option: str,
        points: int = 1,
    ) -> Question:
        try:
            question = Question(
                quiz_id=quiz_id,
                text=text,
                option_a=option_a,
                option_b=option_b,
                option_c=option_c,
                option_d=option_d,
                correct_option=correct_option,
                points=points,
            )
            db.session.add(question)
            db.session.commit()
            return question
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise DAOError(f"Failed to add question: {exc}") from exc

    @staticmethod
    def get_question(question_id: int):
        try:
            return db.session.get(Question, question_id)
        except SQLAlchemyError as exc:
            raise DAOError(f"Failed to fetch question: {exc}") from exc

    @staticmethod
    def get_questions_for_quiz(quiz_id: int):
        try:
            return Question.query.filter_by(quiz_id=quiz_id).all()
        except SQLAlchemyError as exc:
            raise DAOError(f"Failed to list questions: {exc}") from exc

    # ── Results ───────────────────────────────────────────────────────
    @staticmethod
    def save_result(
        quiz_id: int,
        student_id: int,
        score: float,
        total: float,
        percent: float,
        passed: bool,
    ) -> QuizResult:
        try:
            result = QuizResult(
                quiz_id=quiz_id,
                student_id=student_id,
                score=score,
                total=total,
                percent=percent,
                passed=passed,
            )
            db.session.add(result)
            db.session.commit()
            return result
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise DAOError(f"Failed to save quiz result: {exc}") from exc

    @staticmethod
    def get_results_for_student(student_id: int):
        try:
            return QuizResult.query.filter_by(student_id=student_id).all()
        except SQLAlchemyError as exc:
            raise DAOError(f"Failed to fetch results for student: {exc}") from exc

    @staticmethod
    def get_results_for_quiz(quiz_id: int):
        try:
            return QuizResult.query.filter_by(quiz_id=quiz_id).all()
        except SQLAlchemyError as exc:
            raise DAOError(f"Failed to fetch results for quiz: {exc}") from exc
