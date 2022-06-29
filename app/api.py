from typing import List

from fastapi.encoders import jsonable_encoder

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


def get_current_user(
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)
):
    user = decode_jwt(token)
    if not user:
        raise credentials_exception
    db_user = crud.get_user_by_email(db, email=user['sub'])
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


def get_current_active_user(
        current_user: schemas.User = Depends(get_current_user)
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_user_id(
        current_user: schemas.User = Depends(get_current_user)
):
    return current_user.id


@app.post("/token", response_model=Token)
def login_for_access_token(
        db: Session = Depends(get_db),
        form_data: OAuth2PasswordRequestForm = Depends()
):
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise credentials_exception
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


# USERS
@app.post("/users", response_model=schemas.User)
def create_user(
        user: schemas.UserCreate,
        db: Session = Depends(get_db)
):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users", response_model=schemas.User)
def read_users_me(
        current_user: models.User = Depends(get_current_user)
):
    return current_user


# QUIZES
@app.post("/users/quiz", response_model=schemas.Quiz)
def create_quiz_for_user(
        quiz: schemas.QuizCreate,
        user_id: int = Depends(get_user_id),
        db: Session = Depends(get_db)
):
    if not crud.get_user(db, user_id=user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return crud.create_quiz(db=db, quiz=quiz, user_id=user_id)


@app.get("/quizes/{quiz_id}", response_model=schemas.Quiz)
def get_quiz_by_id(
        quiz_id: int,
        user_id: int = Depends(get_user_id),
        db: Session = Depends(get_db)
):
    db_quiz = crud.get_quiz(db, quiz_id=quiz_id, user_id=user_id)
    if db_quiz is None:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return db_quiz


@app.get('/quizes', response_model=List[schemas.Quiz])
def get_all_quizes_for_user(
        user_id: int = Depends(get_user_id),
        db: Session = Depends(get_db)
):
    db_quiz = crud.get_quizes_by_user(db, user_id=user_id)
    if db_quiz is None:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return db_quiz


@app.put('/quizes/{quiz_id}', response_model=schemas.QuizUpdate)
def update_quiz(
        quiz_id: int,
        quiz: schemas.QuizUpdate,
        user_id: int = Depends(get_user_id),
        db: Session = Depends(get_db)
):
    db_quiz = crud.get_quiz(db, quiz_id=quiz_id, user_id=user_id)
    if not db_quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    if db_quiz.is_active:
        raise HTTPException(
            status_code=405,
            detail="You can't update a published quiz."
        )
    if quiz.dict()['is_active']:
        """
        para ativar um quiz é necessário verificar:
         se o quiz tem pelo menos uma pergunta
         se cada pergunta tem pelo menos duas respostas
         se cada pergunta tem pelo menos uma resposta certa
        """
        raise HTTPException(
            status_code=405,
            detail="Quiz can't be activated"  # TODO
        )
    stored_quiz_model = schemas.QuizUpdate(**db_quiz.__dict__)
    update_data = quiz.dict(exclude_unset=True)
    updated_quiz = stored_quiz_model.copy(update=update_data)
    crud.update_quiz(db, jsonable_encoder(updated_quiz), quiz_id)
    return updated_quiz


@app.delete("/quizes/{quiz_id}")
def delete_quiz(
        quiz_id: int,
        user_id: int = Depends(get_user_id),
        db: Session = Depends(get_db)
):
    db_quiz = crud.get_quiz(db, quiz_id=quiz_id, user_id=user_id)
    if not db_quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    crud.delete_quiz(db, quiz_id=quiz_id, user_id=user_id)
    return {'ok': True}


# QUESTIONS
@app.post("/quizes/{quiz_id}/question", response_model=schemas.Question)
def create_question_for_quiz(
        quiz_id: int,
        question: schemas.QuestionCreate,
        user_id: int = Depends(get_user_id),
        db: Session = Depends(get_db)
):
    db_quiz = crud.get_quiz(db, quiz_id=quiz_id, user_id=user_id)
    if not db_quiz:
        raise HTTPException(status_code=404, detail="Quiz not found.")
    if len(db_quiz.questions) >= 10:
        raise HTTPException(status_code=409,
                            detail="Maximum questions for a quiz reached: 10")
    return crud.create_question(db=db, question=question, quiz_id=quiz_id)


@app.get("/questions/{question_id}")
def get_question(
        question_id: int,
        user_id: int = Depends(get_user_id),
        db: Session = Depends(get_db)
):
    db_question = crud.get_question(db, question_id=question_id, user_id=user_id)
    if db_question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return db_question


@app.delete("/questions/{question_id}")
def delete_question(
        question_id: int,
        user_id: int = Depends(get_user_id),
        db: Session = Depends(get_db)
):
    db_question = crud.get_question(db, question_id=question_id, user_id=user_id)
    if not db_question:
        raise HTTPException(status_code=404, detail="Question not found")
    crud.delete_question(db, question_id=question_id)
    return {'ok': True}


# ANSWERS
@app.post("/questions/{question_id}/answer", response_model=schemas.Answer)
def create_anwswer_for_question(
        question_id: int,
        answer: schemas.AnswerCreate,
        user_id: int = Depends(get_user_id),
        db: Session = Depends(get_db)
):
    db_question = crud.get_question(db, question_id=question_id, user_id=user_id)
    if len(db_question.answers) >= 5:
        raise HTTPException(status_code=409,
                            detail="Maximum answers for a question reached: 5")
    return crud.create_answer(db=db, answer=answer,
                              question_id=question_id)


@app.get("/answers/{answer_id}")
def get_all_answers(
        answer_id: int,
        user_id: int = Depends(get_user_id),
        db: Session = Depends(get_db)
):
    db_answer = crud.get_answer(db, answer_id=answer_id, user_id=user_id)
    if not db_answer:
        raise HTTPException(status_code=404, detail="Answer not found")
    return db_answer


@app.delete("/answers/{answer_id}")
def delete_answer(
        answer_id: int,
        user_id: int = Depends(get_user_id),
        db: Session = Depends(get_db)
):
    db_answer = crud.get_answer(db, answer_id, user_id)
    if not db_answer:
        raise HTTPException(status_code=404, detail="Answer not found")
    crud.delete_answer(db, answer_id=answer_id)
    return {'ok': True}


# SOLVE
@app.post("/users/{user_id}/solve", response_model=schemas.Solve)
def create_solve(
        solve: schemas.SolveBase,
        db: Session = Depends(get_db),
        # token: str = Depends(oauth2_scheme)
):
    if not crud.get_user(db, user_id=solve.user_id):
        raise HTTPException(status_code=404, detail="User not found")
    if crud.get_unfinished_solve(db, user_id=solve.user_id):
        raise HTTPException(
            status_code=409,
            detail="User already has an unfinished quiz opened"
        )

    db_solve = models.Solve(
        **solve.dict(),
        quiz_id=1
    )

    return crud.create_solve(db=db, solve=db_solve)

#
# @app.get("/users/{user_id}/solve")
# def get_solve_by_user_id(
#         user_id: int,
#         db: Session = Depends(get_db),
#         # token: str = Depends(oauth2_scheme)
# ):
#     db_solve = crud.get_current_solve(db, user_id=user_id)
#     if db_solve:
#         return crud.get_quiz(db, db_solve.quiz_id)
#     next_quiz = crud.get_first_solvable_quiz_by_user(db, user_id)
#     if not next_quiz:
#         raise HTTPException(status_code=404, detail="No available quizes to solve")
#     return next_quiz
#
