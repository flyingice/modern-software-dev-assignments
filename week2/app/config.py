from dotenv import load_dotenv

load_dotenv()

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = Path(os.environ.get("APP_DATA_DIR", str(BASE_DIR / "data")))
DB_PATH = Path(os.environ.get("APP_DB_PATH", str(DATA_DIR / "app.db")))
OLLAMA_MODEL = os.environ.get("APP_OLLAMA_MODEL", "llama3.1:8b")
