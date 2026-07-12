from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    MAIL_HOST:str
    MAIL_USERNAME:str
    MAIL_PASSWORD:str
    MAIL_PORT:str
    MAIL_FROM_ADDRESS:str
    
    class Config:
        env_file = ".env"

settings = Settings()