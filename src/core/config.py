from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_USER: str
    DATABASE_PASSWORD: str

    database_host: str = "localhost" 
    database_port: str = "5435"
    database_name: str = "store_db"

    groq_api_key: str = ""
    nvidia_api_key: str = ""
    model_name: str = "openai/gpt-oss-120b"
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
        """Builds the complete and security connection string using the corrects variables."""
        return f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.database_host}:{self.database_port}/{self.database_name}"

settings = Settings()