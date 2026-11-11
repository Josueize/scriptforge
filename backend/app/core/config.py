from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # OpenAI configuration
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    # Anthropic Claude configuration
    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-4-6"

    # n8n automation
    n8n_webhook_url: str = ""

    # Database configuration
    database_url: str = ""

    # Frontend configuration
    frontend_url: str = ""

    # Environment configuration
    environment: str = "production"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


settings = Settings()
