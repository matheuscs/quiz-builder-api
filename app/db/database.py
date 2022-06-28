from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from os import environ

Base = declarative_base()

# PROD
SQLALCHEMY_DATABASE_URL = f"postgresql://{environ['POSTGRES_USER']}:{environ['POSTGRES_PASS']}@localhost:5433/{environ['POSTGRES_DB']}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# TESTS
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./quiz-builder-test.db"
testing_engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=testing_engine)


