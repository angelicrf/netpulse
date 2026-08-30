from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


@dataclass(frozen=True)
class Settings:
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    postgres_db: str = os.getenv("POSTGRES_DB", "netpulse")
    postgres_user: str = os.getenv("POSTGRES_USER", "netpulse")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "netpulse")
    grafana_url: str = os.getenv("GRAFANA_URL", "http://localhost:3000")
    grafana_user: str = os.getenv("GRAFANA_USER", "admin")
    grafana_password: str = os.getenv("GRAFANA_PASSWORD", "admin")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
