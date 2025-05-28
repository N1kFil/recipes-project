from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent.parent.parent


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "app" / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "app" / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 60


class Settings(BaseSettings):
    # Настройки БД
    DATABASE_URL: str

    GIGACHAT_API_KEY: str

    auth_jwt: AuthJWT = AuthJWT()

    class Config:
        # Указываем путь к .env файлу явно
        env_file = BASE_DIR / ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True


settings = Settings()
