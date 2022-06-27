from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.auth.auth_bearer import verify_password
from app.auth.auth_handler import create_access_token, decode_jwt, \
    credentials_exception
from app.db import models, schemas
from app.db.crud import get_user_by_email, get_quizes, get_users, create_user, \
    create_user_quiz
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
    user = get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise credentials_exception
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/secure_hello/{name}")
async def hello_name(name: str, token: str = Depends(oauth2_scheme)):
    decode_jwt(token)
    return {"message": f"Hello {name}"}


@app.get("/")
def root():
    return {"message": "i'm alive"}


@app.get("/users")
def getusers(db: Session = Depends(get_db)):
    return get_users(db)


@app.get("/users/<email>")
def getuser(email, db: Session = Depends(get_db)):
    return get_user_by_email(db, email)


@app.get("/quizes")
def getquizes(db: Session = Depends(get_db)):
    return get_quizes(db)


@app.post("/users/{user_id}/quiz/", response_model=schemas.Quiz)
def create_quiz_for_user(
    user_id: int, quiz: schemas.QuizCreate, db: Session = Depends(get_db)
):
    return create_user_quiz(db=db, quiz=quiz, user_id=user_id)


#
# # DB
# @app.post("/users/", response_model=schemas.User)
# def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     db_user = crud.get_user_by_email(db, email=user.email)
#     if db_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
#     return crud.create_user(db=db, user=user)
#
#
# @app.get("/users/", response_model=list[schemas.User])
# def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     users = crud.get_users(db, skip=skip, limit=limit)
#     return users
#
#
# @app.get("/users/{user_id}", response_model=schemas.User)
# def read_user(user_id: int, db: Session = Depends(get_db)):
#     db_user = crud.get_user(db, user_id=user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user
#
#
# @app.post("/users/{user_id}/items/", response_model=schemas.Item)
# def create_item_for_user(
#     user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
# ):
#     return crud.create_user_item(db=db, item=item, user_id=user_id)
#
#
# @app.get("/items/", response_model=list[schemas.Item])
# def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     items = crud.get_items(db, skip=skip, limit=limit)
#     return items
