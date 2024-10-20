from pydantic import Field
from pydantic_settings import BaseSettings


class SMTPSettings(BaseSettings):
    SMTP_SERVER: str = Field("SMTP_SERVER")
    SMTP_PORT: int = Field("SMTP_PORT")
    SMTP_USERNAME: str = Field("SMTP_USERNAME")
    SMTP_PASSWORD: str = Field("SMTP_PASSWORD")
    SMTP_FROM: str = Field("SMTP_FROM")
    USE_SMTP: bool = Field("USE_SMTP")


class EmailServer(BaseSettings):
    api_key: str = Field("API_KEY")


email_server = EmailServer()
smtp_settings = SMTPSettings()
