from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str
    DB_NAME: str = "bernerspace"
    GCP_BUCKET: str
    GCP_CREDENTIALS = settings.GCP_CREDENTIALS or "" 

    class Config:
        env_file = ".env"

settings = Settings()