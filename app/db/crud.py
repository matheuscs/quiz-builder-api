from datetime import datetime
from sqlalchemy.orm import Session

from app.auth.auth_bearer import get_password_hash
from . import models, schemas


# USERS
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        email=user.email,
        hashed_password=get_password_hash(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def delete_user(db: Session, user_id: int):
    db.query(models.User).filter(models.User.id == user_id).delete()
    db.commit()


# QUIZES
def create_quiz(db: Session, quiz: schemas.QuizCreate, user_id: int):
    db_quiz = models.Quiz(**quiz.dict(), user_id=user_id)
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    return db_quiz


def get_quiz(db: Session, quiz_id: int, user_id: int):
    return db.query(models.Quiz).filter(
        models.Quiz.id == quiz_id
    ).filter(
        models.Quiz.user_id == user_id
    ).first()


def get_quizes_by_user(db: Session, user_id: int):
    return db.query(models.Quiz).filter(models.Quiz.user_id == user_id).all()


def update_quiz(db: Session, quiz: schemas.QuizUpdate, quiz_id: int):
    db.query(models.Quiz).filter(models.Quiz.id == quiz_id).update(quiz)
    db.commit()


def delete_quiz(db: Session, quiz_id: int, user_id: int):
    db.query(models.Quiz).filter(
        models.Quiz.id == quiz_id
    ).filter(
        models.Quiz.user_id == user_id
    ).delete()
    db.commit()


# QUESTION
def create_question(db: Session,
                    question: schemas.QuestionCreate,
                    quiz_id: int):
    db_quiz = models.Question(**question.dict(), quiz_id=quiz_id)
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    return db_quiz


def get_question(db: Session, question_id: int, user_id: int):
    return db.query(
        models.Question
    ).join(
        models.Quiz, models.Quiz.id == models.Question.quiz_id
    ).join(
        models.User, models.User.id == models.Quiz.user_id
    ).filter(
        models.Question.id == question_id
    ).filter(
        models.User.id == user_id
    ).first()


def update_question(db: Session,
                    question: schemas.QuestionBase,
                    question_id: int):
    db.query(models.Question).filter(
        models.Question.id == question_id
    ).update(question)
    db.commit()


def delete_question(db: Session, question_id: int):
    db.query(models.Question).filter(
        models.Question.id == question_id
    ).delete()
    db.commit()


# ANSWERS
def create_answer(db: Session, answer: schemas.AnswerCreate, question_id: int):
    db_quiz = models.Answer(**answer.dict(), question_id=question_id)
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    return db_quiz


def get_answer(db: Session, answer_id: int, user_id):
    return db.query(
        models.Answer
    ).join(
        models.Question, models.Question.id == models.Answer.question_id
    ).join(
        models.Quiz, models.Quiz.id == models.Question.quiz_id
    ).join(
        models.User, models.User.id == models.Quiz.user_id
    ).filter(
        models.Answer.id == answer_id
    ).filter(
        models.User.id == user_id
    ).first()


def update_answer(db: Session, answer: schemas.AnswerCreate, answer_id: int):
    db.query(models.Answer).filter(
        models.Answer.id == answer_id
    ).update(answer)
    db.commit()


def delete_answer(db: Session, answer_id: int):
    db.query(models.Answer).filter(models.Answer.id == answer_id).delete()
    db.commit()


# SOLVES
def create_solve(db: Session, solve: schemas.SolveCreate):
    db_solve = models.Solve(
        user_id=solve.user_id,
        quiz_id=solve.quiz_id,
        start_datetime=datetime.now().isoformat(),
    )
    db.add(db_solve)
    db.commit()
    db.refresh(db_solve)
    return db_solve


def get_next_quiz_to_solve(db: Session, user_id: int):
    return db.query(
        models.Quiz
    ).filter(
        models.Quiz.is_active == True
    ).filter(
        models.Quiz.user_id != user_id
    ).outerjoin(
        models.Solve, models.Quiz.id == models.Solve.quiz_id
    ).filter(
        models.Solve.quiz_id == None
    ).first()


def get_finished_solve(db: Session, user_id: int, quiz_id: int):
    return db.query(models.Solve).filter(
        models.Solve.user_id == user_id
    ).filter(
        models.Solve.quiz_id == quiz_id
    ).filter(
        (models.Solve.is_finished == True)
    ).first()


def get_unfinished_solve(db: Session, user_id: int):
    return db.query(models.Solve).filter(
        models.Solve.user_id == user_id
    ).filter(
        models.Solve.is_finished == False
    ).first()
