from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class AnswerBase(BaseModel):
    description: str

    class Config:
        orm_mode = True


class AnswerCreate(AnswerBase):
    is_correct: bool


class Answer(AnswerBase):
    id: int
    question_id: int


class AnswerSolution(BaseModel):
    id: int
    user_answer: bool


class AnswerMock(BaseModel):
    id: int
    is_correct: bool


class QuestionMock(BaseModel):
    id: int
    single_correct_answer: bool
    answers: list[AnswerMock]


class QuestionBase(BaseModel):
    description: str
    single_correct_answer: bool

    class Config:
        orm_mode = True


class Question(QuestionBase):
    id: int
    quiz_id: int
    answers: list[Answer] = []


class QuizBase(BaseModel):
    title: str

    class Config:
        orm_mode = True


class QuizUpdate(QuizBase):
    is_active: bool = False


class Quiz(QuizUpdate):
    id: int
    user_id: int
    questions: list[Question] = []


class UserBase(BaseModel):
    email: str

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    quizes: list[Quiz] = []


class QuestionScoreUpdate(BaseModel):
    question_id: int
    score: int


class QuestionScoreCreate(BaseModel):
    id: int

    class Config:
        orm_mode = True


class QuestionScore(QuestionScoreCreate):
    id: int
    solve_id: int
    question_id: int
    score: int


class SolveBase(BaseModel):
    user_id: int

    class Config:
        orm_mode = True


class SolveCreate(SolveBase):
    quiz_id: int
    quiz: Quiz


class Solve(SolveCreate):
    id: int
    start_datetime: str
    finish_datetime: str
    is_finished: bool
    quiz_score: int
    question_scores: list[QuestionScore] = []


class SolveUpdate(BaseModel):
    id: int
    user_id: int
    quiz_id: int
    start_datetime: str
    finish_datetime: str
    is_finished: bool
    quiz_score: int

    class Config:
        orm_mode = True


class GetSolve(BaseModel):
    id: int
    user_id: int
    quiz_id: int
    start_datetime: str
    finish_datetime: str
    is_finished: bool
    quiz_score: int
    question_scores: list[QuestionScore] = []

    class Config:
        orm_mode = True

