"""Configuración del proyecto cargada desde variables de entorno."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    postgres_user: str = "crypto"
    postgres_password: str = "crypto"
    postgres_db: str = "crypto_pulse"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    coingecko_base_url: str = "https://api.coingecko.com/api/v3"
    coingecko_vs_currency: str = "usd"
    coingecko_top_n: int = 50

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
