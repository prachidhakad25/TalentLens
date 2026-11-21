import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./talentlens.db")
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    # Keep the SQLite file in the backend directory for predictable local runs.
    if DATABASE_URL == "sqlite:///./talentlens.db":
        DATABASE_URL = f"sqlite:///{(Path(__file__).resolve().parents[1] / 'talentlens.db').as_posix()}"
else:
    connect_args = {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
