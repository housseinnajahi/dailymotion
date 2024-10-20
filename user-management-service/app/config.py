from pydantic import Field
from pydantic_settings import BaseSettings


class PostgresSettings(BaseSettings):
    POSTGRES_USER: str = Field(env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(env="POSTGRES_DB")
    POSTGRES_PORT: str = Field(env="POSTGRES_PORT", default="5432")


class EmailServiceSettings(BaseSettings):
    API_KEY: str = Field(env="API_KEY")
    EMAIL_SERVICE_URL: str = Field(env="EMAIL_SERVICE_URL")


postgres_settings = PostgresSettings()
email_service_settings = EmailServiceSettings()
