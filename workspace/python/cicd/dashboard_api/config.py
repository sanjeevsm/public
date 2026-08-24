from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache

_HERE = Path(__file__).parent


class Settings(BaseSettings):
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "info"
    export_dir: str = str(_HERE / "exports")
    cache_ttl: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
