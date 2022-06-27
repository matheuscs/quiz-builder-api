from app.db import crud
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.auth_bearer import verify_password
from app.auth.auth_handler import create_access_token, decode_jwt, \
    credentials_exception
from app.db import models, schemas
from app.db.database import engine, SessionLocal
from app.db.schemas import Token

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/token", response_model=Token)
async def login_for_access_token(
        db: Session = Depends(get_db),
        form_data: OAuth2PasswordRequestForm = Depends()):
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise credentials_exception
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/alive")
def i_am_alive():
    return {"msg": "i'm alive"}


@app.get("/alive_secure")
async def i_am_alive_and_secure(token: str = Depends(oauth2_scheme)):
    decode_jwt(token)
    return {"msg": "i'm alive and secure"}


# USERS
@app.post("/users", response_model=schemas.User)
def create_user(user: schemas.UserCreate,
                db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/{user_id}", response_model=schemas.User)
def get_user_by_id(user_id: int,
                   db: Session = Depends(get_db),
                   token: str = Depends(oauth2_scheme)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get("/users_by_email/{email}", response_model=schemas.User)
def get_user_by_email(email,
                      db: Session = Depends(get_db),
                      token: str = Depends(oauth2_scheme)):
    return crud.get_user_by_email(db, email)


@app.get("/users")
def get_all_users(db: Session = Depends(get_db),
                  token: str = Depends(oauth2_scheme)):
    return crud.get_users(db)


# QUIZES
@app.post("/user/{user_id}/quiz", response_model=schemas.Quiz)
def create_quiz_for_user(
        user_id: int,
        quiz: schemas.QuizCreate,
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)):
    return crud.create_user_quiz(db=db, quiz=quiz, user_id=user_id)


@app.get("/quiz/{quiz_id}", response_model=schemas.Quiz)
def get_quiz_by_id(quiz_id: int,
                   db: Session = Depends(get_db),
                   token: str = Depends(oauth2_scheme)):
    db_quiz = crud.get_quiz(db, quiz_id=quiz_id)
    if db_quiz is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return db_quiz


@app.get("/quizes")
def get_all_quizes(db: Session = Depends(get_db),
                   token: str = Depends(oauth2_scheme)):
    return crud.get_quizes(db)


# QUESTIONS
@app.post("/quiz/{quiz_id}/question", response_model=schemas.Question)
def create_question_for_quiz(
        quiz_id: int,
        question: schemas.QuestionCreate,
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)
):
    db_quiz = get_quiz_by_id(quiz_id, db)
    if len(db_quiz.questions) >= 10:
        raise HTTPException(status_code=403,
                            detail="Maximum questions for a quiz reached: 10")
    return crud.create_quiz_question(db=db, question=question, quiz_id=quiz_id)


@app.get("/question/{question_id}", response_model=schemas.Question)
def get_question_by_id(question_id: int,
                       db: Session = Depends(get_db),
                       token: str = Depends(oauth2_scheme)):
    db_question = crud.get_question(db, question_id=question_id)
    if db_question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return db_question


@app.get("/questions")
def get_all_questions(db: Session = Depends(get_db),
                      token: str = Depends(oauth2_scheme)):
    return crud.get_questions(db)


# ANSWERS
@app.post("/question/{question_id}/answer", response_model=schemas.Answer)
def create_anwswer_for_question(
        question_id: int,
        answer: schemas.AnswerCreate,
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)
):
    db_question = get_question_by_id(question_id, db)
    print(f'{db_question.answers}')
    if len(db_question.answers) >= 5:
        raise HTTPException(status_code=403,
                            detail="Maximum answers for a question reached: 5")
    return crud.create_question_answer(db=db, answer=answer,
                                       question_id=question_id)


@app.get("/answers")
def get_all_answers(db: Session = Depends(get_db),
                    token: str = Depends(oauth2_scheme)):
    return crud.get_answers(db)
