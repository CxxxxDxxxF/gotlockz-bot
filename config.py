# config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    discord_token: str = Field(..., env="DISCORD_TOKEN")
    sheet_id:       str = Field(..., env="SHEET_ID")
    google_sheets_creds:     str | None = Field(None, env="GOOGLE_SHEETS_CREDS")
    google_sheets_creds_b64: str | None = Field(None, env="GOOGLE_SHEETS_CREDS_B64")

    model_config = SettingsConfigDict(
        env_file       = ".env",
        env_file_encoding = "utf-8",
    )

settings = Settings()
