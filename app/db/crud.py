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


# def get_user_by_quiz(db: Session, email: str):
#     return db.query(models.User).filter(models.User.quizes == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


# QUIZES
def create_user_quiz(db: Session, quiz: schemas.QuizCreate, user_id: int):
    db_quiz = models.Quiz(**quiz.dict(), user_id=user_id)
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    return db_quiz


def get_quiz(db: Session, quiz_id: int):
    return db.query(models.Quiz).filter(models.Quiz.id == quiz_id).first()


def get_users_quizes(db: Session, user_id: int):
    return db.query(models.Quiz).filter(models.Quiz.user_id == user_id).all()


def update_quiz(db: Session, quiz: schemas.QuizUpdate, quiz_id: int):
    db.query(models.Quiz).filter(models.Quiz.id == quiz_id).update(quiz)
    db.commit()


# QUESTION
def create_quiz_question(db: Session, question: schemas.QuestionCreate, quiz_id: int):
    db_quiz = models.Question(**question.dict(), quiz_id=quiz_id)
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    return db_quiz


def get_question(db: Session, question_id: int):
    return db.query(models.Question).filter(
        models.Question.id == question_id
    ).first()


def get_questions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Question).offset(skip).limit(limit).all()


# ANSWERS
def create_question_answer(db: Session, answer: schemas.AnswerCreate, question_id: int):
    db_quiz = models.Answer(**answer.dict(), question_id=question_id)
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    return db_quiz


def get_answers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Answer).offset(skip).limit(limit).all()

