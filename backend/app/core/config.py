from pydantic_settings import BaseSettings
from pydantic import AnyUrl


class Settings(BaseSettings):
    app_name: str = "Chain Of Record"
    api_v1_prefix: str = "/api/v1"
    environment: str = "local"  # local | dev | prod
    database_url: AnyUrl        # <- this is what was missing
    log_level: str = "INFO"

    @property
    def is_development(self) -> bool:
        return self.environment in ["local", "dev"]
    
    @property
    def is_production(self) -> bool:
        return self.environment == "prod"

    class Config:
        env_file = ".env"
        env_prefix = ""
        case_sensitive = False


settings = Settings()