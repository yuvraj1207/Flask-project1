from dao.quiz_dao import QuizDAO
from dao.enrollment_dao import EnrollmentDAO

class QuizService:
    @staticmethod
    def process_and_score_quiz(quiz_id, student_id, user_answers):
        quiz = QuizDAO.get_quiz_by_id(quiz_id)
        if not quiz or not quiz.questions:
            raise ValueError("Quiz contains no questions.")

        total_questions = len(quiz.questions)
        correct_count = 0

        # Grade student choices against DB records
        for question in quiz.questions:
            submitted = user_answers.get(str(question.id))
            if submitted and submitted.upper() == question.correct_option:
                correct_count += 1

        # Calculate percentage score
        score_percentage = (correct_count / total_questions) * 100.0

        # Save result record
        result = QuizDAO.save_quiz_result(
            quiz_id=quiz_id,
            student_id=student_id,
            score=round(score_percentage, 2),
            total_questions=total_questions
        )

        # Update student course progress
        EnrollmentDAO.update_progress(student_id, quiz.course_id, round(score_percentage, 2))

        return result, correct_count, total_questions