from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # -----------------------------------------
    # OpenAI configuration
    # -----------------------------------------
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    # -----------------------------------------
    # Anthropic Claude configuration
    # -----------------------------------------
    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-4-6"

    # -----------------------------------------
    # AI pipeline configuration
    # -----------------------------------------
    max_retries: int = 3
    request_timeout: int = 60

    # -----------------------------------------
    # n8n automation configuration
    # -----------------------------------------
    n8n_webhook_url: str = ""
    n8n_webhook_token: str = ""

    # -----------------------------------------
    # PostgreSQL database configuration
    # -----------------------------------------
    database_url: str = "postgresql://user:password@localhost:5432/scriptforge"

    # -----------------------------------------
    # Pydantic environment configuration
    # -----------------------------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
