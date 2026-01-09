from pathlib import Path
from typing import Final

APP: Final = "MERCEDES"
BASE_DIR: Final = Path(__file__).resolve().parent

OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "gpt-oss:20b"
