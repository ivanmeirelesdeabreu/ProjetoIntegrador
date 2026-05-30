from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR.parent / "data" / "raw"
LOG_FILE = BASE_DIR / "log_erros_importacao.txt"