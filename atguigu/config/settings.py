from pathlib import Path

from pydantic_settings import SettingsConfigDict, BaseSettings

PROJECT_DIR = Path(__file__).resolve().parents[2]

ENV_FILE_PATH = PROJECT_DIR / ".env"

print(ENV_FILE_PATH)


class Settings(BaseSettings):
    llm_model: str
    llm_base_url: str
    llm_api_key: str
    commerce_api_base_url: str
    database_url: str
    app_host: str
    app_port: int  # APP_PORT=18082 自动转换成int类型（能转 转不了就报错）

    model_config = SettingsConfigDict(env_file=ENV_FILE_PATH, env_file_encoding="utf-8")


settings = Settings()  # type:ignore

if __name__ == '__main__':
    print(settings.llm_model)
    print(settings.llm_base_url)
    print(settings.llm_api_key)
    print(type(settings.app_port))
