from pydantic import BaseModel
from typing import Union


class Token(BaseModel):
    access_token: str
    token_type: str


class ItemBase(BaseModel):
    title: str
    description: Union[str, None] = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class QuizBase(BaseModel):
    title: str


class QuizCreate(QuizBase):
    is_active = bool


class Quiz(QuizBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


class QuestionBase(BaseModel):
    description: str
    single_correct_answer: bool


class QuestionCreate(QuestionBase):
    is_active = bool


class Question(QuestionBase):
    id: int
    quiz_id: int

    class Config:
        orm_mode = True


class AnswerBase(BaseModel):
    description: str
    is_correct: bool


class AnswerCreate(AnswerBase):
    is_active = bool


class Answer(AnswerBase):
    id: int
    question_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    items: list[Item] = []

    class Config:
        orm_mode = True