# This config file defines waht setting the application needs
from pathlib import Path
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):
  model_config = SettingsConfigDict(
    env_file = BASE_DIR/".env",
    env_file_encoding = "utf-8"
  )

  secret_key: SecretStr
  algorithm: str = "HS256" # Standard for JSON web token
  access_token_expire_minutes: int = 30

# Setting instance - Loaded from .env file
settings = Settings() # type: ignore[call-arg]
