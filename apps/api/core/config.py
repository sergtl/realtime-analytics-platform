from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    debug: bool = False
    pool_pre_ping: bool = False

    stream_key: str = "events"
    consumer_group: str = "analytics-ingestors"
    num_workers: int = 5
    redis_url: str = "redis://localhost:6379/0"

    supported_event_schema_versions: set[str] = {"1.0.0"}
    max_event_body_bytes: int = 256_000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
