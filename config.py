import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = str(BASE_DIR / "database.db")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
