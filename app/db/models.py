from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    quizes = relationship("Quiz", cascade="all, delete", backref="user")
    solves = relationship("Solve", cascade="all, delete", backref="user")


class Quiz(Base):
    __tablename__ = "quizes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    is_active = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'))
    questions = relationship("Question", cascade="all, delete", backref="quiz")
    solves = relationship("Solve", cascade="all, delete", backref="quiz")


class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    single_correct_answer = Column(Boolean, default=True)
    quiz_id = Column(Integer, ForeignKey("quizes.id", ondelete='CASCADE'))
    answers = relationship("Answer", cascade="all, delete", backref="question")


class Answer(Base):
    __tablename__ = "answers"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    is_correct = Column(Boolean, default=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete='CASCADE'))


class Solve(Base):
    __tablename__ = "solves"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'))
    quiz_id = Column(Integer, ForeignKey("quizes.id", ondelete='CASCADE'))
    start_datetime = Column(String, default='')
    finish_datetime = Column(String, default='')
    is_finished = Column(Boolean, default=False)
    score = Column(Integer, default=0)

