from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/dashboard_dev"
    database_pool_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/dashboard_dev"

    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_jwt_secret: str = ""

    auth_enforcement_enabled: bool = False
    rls_enabled: bool = False

    notifier_type: str = "noop"
    cache_provider: str = "inmemory"

    log_level: str = "INFO"
    environment: str = "development"


settings = Settings()
