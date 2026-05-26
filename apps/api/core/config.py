from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    debug: bool = False
    pool_pre_ping: bool = False

    stream_key: str = "events"
    consumer_group: str = "analytics-ingestors"
    num_workers: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
