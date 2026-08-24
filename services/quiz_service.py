from dao.quiz_dao import QuizDAO
from dao.user_dao import DAOError

VALID_OPTIONS = {"a", "b", "c", "d"}


class QuizServiceError(Exception):
    """Raised for all quiz business-logic failures."""


class QuizService:

    @staticmethod
    def create_quiz(module_id: int, title: str, pass_percent: float = 50.0):
        if not title or not title.strip():
            raise QuizServiceError("Quiz title is required.")
        if not (0.0 <= pass_percent <= 100.0):
            raise QuizServiceError("pass_percent must be between 0 and 100.")
        try:
            return QuizDAO.create_quiz(module_id, title.strip(), pass_percent)
        except DAOError as exc:
            raise QuizServiceError(str(exc)) from exc

    @staticmethod
    def get_quiz(quiz_id: int):
        try:
            quiz = QuizDAO.get_quiz(quiz_id)
        except DAOError as exc:
            raise QuizServiceError(str(exc)) from exc
        if not quiz:
            raise QuizServiceError("Quiz not found.")
        return quiz

    @staticmethod
    def list_quizzes(module_id: int):
        try:
            return QuizDAO.get_quizzes_for_module(module_id)
        except DAOError as exc:
            raise QuizServiceError(str(exc)) from exc

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
    ):
        QuizService.get_quiz(quiz_id)               # ensures quiz exists

        if not text or not text.strip():
            raise QuizServiceError("Question text is required.")

        correct_option = (correct_option or "").strip().lower()
        if correct_option not in VALID_OPTIONS:
            raise QuizServiceError("correct_option must be one of: a, b, c, d.")

        if points < 1:
            raise QuizServiceError("Points must be at least 1.")

        try:
            return QuizDAO.add_question(
                quiz_id, text.strip(),
                option_a, option_b, option_c, option_d,
                correct_option, points,
            )
        except DAOError as exc:
            raise QuizServiceError(str(exc)) from exc

    @staticmethod
    def get_questions(quiz_id: int):
        try:
            return QuizDAO.get_questions_for_quiz(quiz_id)
        except DAOError as exc:
            raise QuizServiceError(str(exc)) from exc

    @staticmethod
    def evaluate_attempt(quiz_id: int, student_id: int, answers: dict):
        """
        Score a quiz attempt.
        answers: {str(question_id): selected_option ('a'|'b'|'c'|'d')}
        Returns the persisted QuizResult.
        """
        quiz      = QuizService.get_quiz(quiz_id)
        questions = QuizService.get_questions(quiz_id)

        if not questions:
            raise QuizServiceError("This quiz has no questions yet.")

        total_points = 0
        score        = 0

        for question in questions:
            total_points += question.points
            # Accept both str and int keys
            selected = answers.get(str(question.id)) or answers.get(question.id)
            if selected and str(selected).strip().lower() == question.correct_option:
                score += question.points

        percent = round((score / total_points) * 100, 2) if total_points else 0.0
        passed  = percent >= quiz.pass_percent

        try:
            return QuizDAO.save_result(
                quiz_id=quiz_id,
                student_id=student_id,
                score=float(score),
                total=float(total_points),
                percent=percent,
                passed=passed,
            )
        except DAOError as exc:
            raise QuizServiceError(str(exc)) from exc

    @staticmethod
    def get_results_for_student(student_id: int):
        try:
            return QuizDAO.get_results_for_student(student_id)
        except DAOError as exc:
            raise QuizServiceError(str(exc)) from exc

    @staticmethod
    def get_results_for_quiz(quiz_id: int):
        try:
            return QuizDAO.get_results_for_quiz(quiz_id)
        except DAOError as exc:
            raise QuizServiceError(str(exc)) from exc
