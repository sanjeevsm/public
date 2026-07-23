from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache

_HERE = Path(__file__).parent


class Settings(BaseSettings):
    gitlab_url: str = ""
    gitlab_token: str = ""
    gitlab_project_ids: str = ""
    gitlab_project_limit: int = 20
    app_host: str = "0.0.0.0"
    app_port: int = 8090
    log_level: str = "info"
    export_dir: str = str(_HERE / "exports")
    cache_ttl: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
