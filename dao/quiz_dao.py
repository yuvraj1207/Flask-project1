from config.database import db
from models.quiz import Quiz, Question, QuizResult

class QuizDAO:
    @staticmethod
    def create_quiz(course_id, title):
        quiz = Quiz(course_id=course_id, title=title)
        db.session.add(quiz)
        db.session.commit()
        return quiz

    @staticmethod
    def get_quiz_by_id(quiz_id):
        return Quiz.query.get(quiz_id)

    @staticmethod
    def add_question(quiz_id, question_text, option_a, option_b, option_c, option_d, correct_option):
        question = Question(
            quiz_id=quiz_id,
            question_text=question_text,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_option=correct_option.upper()
        )
        db.session.add(question)
        db.session.commit()
        return question

    @staticmethod
    def save_quiz_result(quiz_id, student_id, score, total_questions):
        result = QuizResult(
            quiz_id=quiz_id,
            student_id=student_id,
            score=score,
            total_questions=total_questions
        )
        db.session.add(result)
        db.session.commit()
        return result

    @staticmethod
    def get_student_results(student_id):
        return QuizResult.query.filter_by(student_id=student_id).all()