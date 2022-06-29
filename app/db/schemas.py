from pydantic import BaseModel
from typing import Union


class Token(BaseModel):
    access_token: str
    token_type: str


class AnswerBase(BaseModel):
    description: str


class AnswerCreate(AnswerBase):
    is_correct: bool


class Answer(AnswerBase):
    id: int
    question_id: int

    class Config:
        orm_mode = True


class QuestionBase(BaseModel):
    description: str
    single_correct_answer: bool


class QuestionCreate(QuestionBase):
    ...


class Question(QuestionBase):
    id: int
    quiz_id: int
    answers: list[Answer] = []

    class Config:
        orm_mode = True


class QuizBase(BaseModel):
    title: str


class QuizCreate(QuizBase):
    ...


class QuizUpdate(QuizCreate):
    is_active: bool = False


class Quiz(QuizUpdate):
    id: int
    user_id: int
    questions: list[Question] = []

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    quizes: list[Quiz] = []

    class Config:
        orm_mode = True
