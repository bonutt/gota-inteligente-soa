"""Configurações da aplicação, lidas de variáveis de ambiente ou do arquivo .env."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "sqlite:///./gota_inteligente.db"
    api_titulo: str = "Gota Inteligente API"
    api_versao: str = "1.0.0"

    # Parâmetros das regras de negócio
    limite_chuva_alta: int = 70          # % de chance de chuva a partir da qual vale esperar
    umidade_solo_critica: float = 15.0   # abaixo disso irriga mesmo com chuva prevista
    lamina_irrigacao_mm: float = 5.0     # lâmina d'água de uma irrigação (para estimar economia)


settings = Settings()
