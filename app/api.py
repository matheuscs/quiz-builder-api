from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from fastapi import FastAPI, Depends, HTTPException, status
from decouple import config

from app.auth.auth_handler import create_access_token, decode_jwt, \
    credentials_exception
from app.model import Token, TokenData, User, UserInDB


app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

JWT_SECRET = config("SECRET_KEY")
JWT_ALGORITHM = config("ALGORITHM")


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$p05BVViYxj1LwXKMx4WSle4yNZwFbr95gyrMmfmInapEiAlMFfFRa",  # secret
        "disabled": False,
    },
    "qw": {
        "username": "qw",
        "full_name": "lazy",
        "email": "lazy@example.com",
        "hashed_password": "$2b$12$bFQL1aAh0MfCbGPMpKyFxuAqDcq8vo0gNG/EUzEx3pbS/eprzvUim",  # 12
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "$2b$12$uecHA3IsecPlHI2H2O4g2efmHTnkNxry/8sgXUzl4E4jMzkWqlixa",  # secret2
        "disabled": True,
    },
}


async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_jwt(token)
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    token_data = TokenData(username=username)
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/secure_hello/{name}")
async def hello_name(name: str, token: str = Depends(oauth2_scheme)):
    return {"message": f"Hello {name}"}


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
