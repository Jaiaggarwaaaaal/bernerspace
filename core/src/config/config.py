from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str
    DB_NAME: str = "bernerspace"
    GCP_BUCKET: str
    GOOGLE_APPLICATION_CREDENTIALS: str 

    class Config:
        env_file = ".env"

settings = Settings()