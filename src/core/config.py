from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Lidos do .env automaticamente
    DATABASE_USER: str
    DATABASE_PASSWORD: str

    # Valores padrão
    database_host: str = "localhost" 
    database_port: str = "5435"
    database_name: str = "store_db"

    groq_api_key: str = ""
    nvidia_api_key: str = ""
    model_name: str = "meta/llama-3.1-70b-instruct"
    mcp_server_url: str = "http://localhost:8080/sse"
    api_base: str = "/api/v1"

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )

    @property
    def database_url(self) -> str:
        """Monta a string de conexão completa e segura usando as variáveis corretas."""
        return f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.database_host}:{self.database_port}/{self.database_name}"

settings = Settings()