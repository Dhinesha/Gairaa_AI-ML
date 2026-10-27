from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Root directory of the project
ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PROJECT_NAME: str = "AI DevOps Assistant using MCP"
    PROJECT_VERSION: str = "1.0.0"

    GEMINI_API_KEY: str = ""
    GITHUB_TOKEN: str = ""

    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = True

    DEMO_REPO_PATH: Path = ROOT_DIR / "demo_repo"
    ROOT_DIR: Path = ROOT_DIR


settings = Settings()
