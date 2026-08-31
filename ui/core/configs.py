from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_host: str = "localhost" 
    api_port: str = "5435"
    api_base: str = "/api/v1"

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )

    @property
    def api_url(self) -> str:
        return f"http://{self.api_host}:{self.api_port}{self.api_base}"


settings = Settings()