from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    anthropic_api_key: str
    openai_model: str = "gpt-4o"
    claude_model: str = "claude-sonnet-4-20250514"
    max_retries: int = 3
    request_timeout: int = 60
    n8n_webhook_url: str = ""
    database_url: str = "postgresql://user:password@localhost:5432/scriptforge"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()