from __future__ import annotations

import logging
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.models import Base

LOGGER = logging.getLogger(__name__)
DB_PATH = Path(__file__).resolve().parent.parent / "memory.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    try:
        Base.metadata.create_all(bind=engine)
        LOGGER.info("Database initialized at %s", DB_PATH)
    except Exception as exc:
        LOGGER.exception("Failed to initialize SQLite database: %s", exc)
        raise
