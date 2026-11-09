from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./syntra.db"  # laptop-friendly default for local dev
    secret_key: str = "dev-only-change-me"
    access_token_minutes: int = 60 * 12
    allow_registration: bool = False
    frontend_dir: str = "../frontend"


settings = Settings()
