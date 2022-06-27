from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config

SQLALCHEMY_DATABASE_URL = f"postgresql://{config('POSTGRES_USER')}:{config('POSTGRES_PASS')}@localhost:5433/{config('POSTGRES_DB')}"
# SQLALCHEMY_DATABASE_URL = "sqlite:///./quiz-builder.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
