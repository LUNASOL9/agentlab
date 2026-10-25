from pydantic_settings import BaseSettings, SettingsConfigDict


# application.yml 역할이에요. 환경변수나 backend/.env 파일에서 값을 읽어요.
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./agentlab.db"


settings = Settings()
