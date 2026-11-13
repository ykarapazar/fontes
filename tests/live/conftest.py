"""Live tests use the same API keys as the server: load the checkout's .env (set vars win)."""
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
