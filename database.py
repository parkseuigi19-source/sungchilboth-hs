from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# 환경 변수에서 DB URL 가져오기 (기본값: SQLite)
DB_URL = os.getenv("DB_URL", "sqlite:///./sungchibot.db")

# MySQL 연결 시 추가 설정 (pool_recycle 등)
connect_args = {}
if "sqlite" in DB_URL:
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DB_URL, 
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=3600
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
