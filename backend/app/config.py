from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./astravital.db"
    cors_origins: str = "http://localhost:3000"
    mission_name: str = "Simulated Mars Transit"
    mission_day: int = 42
    communication_delay_minutes: float = 8.0

    model_config = SettingsConfigDict(env_file=".env", env_prefix="ASTRAVITAL_")

    @property
    def cors_origin_list(self) -> list[str]:
        return [value.strip() for value in self.cors_origins.split(",") if value.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

