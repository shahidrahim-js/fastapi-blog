# This config file defines waht setting the application needs

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
  model_config = SettingsConfigDict(
    env_file = ".env",
    env_file_encoding = "utf-8"
  )

  secret_key: SecretStr
  algorithm: str = "HS256" # Standard for JSON web token
  access_token_expire_minutes: int = 30

# Setting instance - Loaded from .env file
settings = Settings() # type: ignore[call-arg]
