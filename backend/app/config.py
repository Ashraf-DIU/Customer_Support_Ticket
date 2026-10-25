import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _bool(name: str, default: str) -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes"}


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL") or f"sqlite:///{BASE_DIR / 'supportiq.db'}"
    frontend_urls: tuple = tuple(
        u.strip().rstrip("/") for u in os.getenv("FRONTEND_URL", "http://localhost:3000").split(",") if u.strip()
    )
    allow_vercel_previews: bool = _bool("ALLOW_VERCEL_PREVIEWS", "true")
    model_dir: Path = (BASE_DIR / os.getenv("MODEL_DIR", "artifacts")).resolve()
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "claude-sonnet-5-5")
    confidence_threshold: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.40"))
    allow_demo_seed: bool = _bool("ALLOW_DEMO_SEED", "true")


settings = Settings()
