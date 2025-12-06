# database/database.py
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "app.db"
DATABASE_URL = f"sqlite:///{DB_PATH.as_posix()}"

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def db_exists() -> bool:
    return DB_PATH.exists()

def init_db_if_exists(base):
    """
    Do NOT create DB if it doesn't exist: only create tables if file exists.
    Returns True if DB existed and tables ready, False if DB missing.
    """
    if not db_exists():
        return False
    base.metadata.create_all(bind=engine)
    return True

def create_db(base):
    """
    Create data dir and DB file + tables. Returns True on success.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    base.metadata.create_all(bind=engine)
    return True
