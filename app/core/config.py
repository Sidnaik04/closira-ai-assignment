from pydantic_settings import BaseSettings, SettingsConfigDict

# Global debug flag
DEBUG = False


class Settings(BaseSettings):
    DEFAULT_PROVIDER: str = "gemini"

    OPENAI_API_KEY: str | None = None
    GOOGLE_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None

    MODEL_NAME: str = "gemini-2.5-flash"

    DATABASE_URL: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
