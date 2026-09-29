from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://appuser:apppassword@localhost:5434/webdatadb"
    user_agent: str = "SmartWebDataPipeline/1.0 (+portfolio project)"
    fetch_timeout_seconds: float = 10.0
    max_response_bytes: int = 2_000_000
    respect_robots_txt: bool = True
    openai_api_key: str | None = None
    openai_model: str = "gpt-5.5"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
