from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    discord_token: str = Field(..., env='DISCORD_TOKEN')
    sheet_id: str = Field(..., env='SHEET_ID')
    google_sheets_creds: str = Field(None, env='GOOGLE_SHEETS_CREDS')
    google_sheets_creds_b64: str = Field(None, env='GOOGLE_SHEETS_CREDS_B64')

    class Config:
        case_sensitive = True

settings = Settings()
