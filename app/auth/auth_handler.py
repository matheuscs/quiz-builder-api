from os import environ
from datetime import datetime, timedelta

from fastapi import HTTPException
from jose import jwt, JWTError
from starlette import status

JWT_SECRET = environ["SECRET_KEY"]
JWT_ALGORITHM = environ["ALGORITHM"]
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = environ["ACCESS_TOKEN_EXPIRE_MINUTES"]

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def create_access_token(data: dict):
    to_encode = data.copy()
    expires_delta = timedelta(minutes=int(JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_jwt(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError:
        raise credentials_exception
