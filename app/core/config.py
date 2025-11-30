from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    #  automatically read these names from your .env file
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # Default 7 days

    # This configures to look at the .env file
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()