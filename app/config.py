from pydantic import BaseSettings


class Settings(BaseSettings):
    DATABASE_PASSWORD: str
    DATABASE_NAME: str
    DATABASE_USERNAME: str
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: str
    SECRET_KEY: str
    TIMEOUT_MINUTES: int
    ALGORITHM: str

    class Config:
        env_file = ".env"


settings = Settings()
