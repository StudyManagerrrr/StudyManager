from pathlib import Path
import secrets

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT=Path(__file__).resolve().parents[3]

class Settings(BaseSettings):
    app_env: str = 'development'
    database_url: str = ''
    ai_provider: str = ''
    ai_api_key: str = ''
    ai_base_url: str = ''
    ai_model: str = ''
    host: str = '127.0.0.1'
    port: int = 8765
    log_level: str = 'INFO'
    jwt_secret: str | None = None
    frontend_origin: str = 'http://localhost:5173'

    model_config = SettingsConfigDict(
        env_file=ROOT / '.env', extra='ignore', case_sensitive=False
    )

    @model_validator(mode='after')
    def validate_jwt_secret(self):
        environment = self.app_env.lower()
        if not self.jwt_secret:
            if environment not in {'development', 'dev', 'test'}:
                raise ValueError('JWT_SECRET must be configured outside development')
            # A random, process-local dev key avoids a reusable hard-coded signing key.
            self.jwt_secret = secrets.token_urlsafe(48)
        elif len(self.jwt_secret) < 32 or any(
            marker in self.jwt_secret.lower()
            for marker in ('change-me', 'replace-with', 'placeholder', 'example')
        ):
            raise ValueError('JWT_SECRET must contain at least 32 non-placeholder characters')
        return self

settings=Settings()
