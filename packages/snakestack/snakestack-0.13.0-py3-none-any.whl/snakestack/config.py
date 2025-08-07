from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from snakestack import version


class SnakeStackSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    snakestack_log_level: str = Field(
        default="INFO",
        description="Logging level for the application (e.g., DEBUG, INFO, WARNING, ERROR)."
    )

    snakestack_default_formatter: str = Field(
        default="default",
        description=""
    )

    snakestack_version: str = Field(
        default=version.__version__,
        description=""
    )

    snakestack_mongodb_url: str = Field(
        default="mongodb://localhost:27017",
        description=""
    )

    snakestack_mongodb_dbname: str = Field(
        default="snakestack",
        description=""
    )

    snakestack_otel_disabled: bool = Field(
        default=False,
        description=(
            "Disables only the OpenTelemetry instrumentation provided by the SnakeStack library. "
            "This allows external OpenTelemetry configurations (e.g., opentelemetry-bootstrap or custom distro) "
            "to take full control over instrumentation without duplication. "
            "Equivalent to setting the environment variable SNAKESTACK_OTEL_DISABLED=true."
        )
    )

    pubsub_project_id: str = Field(
        default="snakestack-project",
        description=""
    )

    otel_sdk_disabled: bool = Field(
        default=False,
        description=(
            "Disables the entire OpenTelemetry SDK, including all automatic and manual instrumentation. "
            "Equivalent to setting the environment variable OTEL_SDK_DISABLED=true. "
            "When enabled, no traces, metrics, or logs will be generated or exported by the OpenTelemetry SDK."
        )
    )


@lru_cache
def get_settings() -> SnakeStackSettings:
    return SnakeStackSettings()


settings = get_settings()
