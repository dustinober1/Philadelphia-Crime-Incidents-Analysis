"""Base configuration settings using pydantic-settings."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

# Resolve repo root
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class GlobalConfig(BaseSettings):
    """Global shared configuration for all analyses."""

    model_config = SettingsConfigDict(
        yaml_file="config/global.yaml",
        env_prefix="CRIME_",
        env_nested_delimiter="__",
        extra="ignore",  # Allow extra fields from YAML
    )

    # Data paths
    crime_data_path: Path = Field(default=_REPO_ROOT / "data" / "crime_incidents_combined.parquet")
    boundaries_dir: Path = Field(default=_REPO_ROOT / "data" / "boundaries")
    external_dir: Path = Field(default=_REPO_ROOT / "data" / "external")

    # Output settings
    output_dir: Path = Field(default=_REPO_ROOT / "reports")
    dpi: int = Field(default=300, ge=72, le=600)
    output_format: str = Field(default="png", pattern="^(png|svg|pdf)$")

    # Performance
    fast_sample_frac: float = Field(default=0.1, ge=0.01, le=1.0)
    cache_enabled: bool = True

    # Logging
    log_level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR)$")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,  # noqa: ARG003
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Configure source priority: CLI > env > YAML > defaults."""
        # Note: file_secret_settings is not used but required by pydantic-settings signature
        return (
            init_settings,  # CLI arguments (highest priority)
            env_settings,  # Environment variables
            YamlConfigSettingsSource(settings_cls),  # YAML files
            dotenv_settings,  # .env files (lowest priority)
        )


class BaseConfig(BaseSettings):
    """Base class for all analysis-specific configs."""

    model_config = SettingsConfigDict(
        env_prefix="CRIME_",
        env_nested_delimiter="__",
        extra="ignore",  # Allow extra fields from YAML
    )

    # Global settings (inherited from GlobalConfig)
    output_dir: Path = Field(default=_REPO_ROOT / "reports")
    dpi: int = Field(default=300, ge=72, le=600)
    output_format: str = Field(default="png", pattern="^(png|svg|pdf)$")
    fast_sample_frac: float = Field(default=0.1, ge=0.01, le=1.0)
    cache_enabled: bool = True
    log_level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR)$")

    # Analysis version
    version: str = "v1.0"

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,  # noqa: ARG003
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Configure source priority: CLI > env > YAML > defaults."""
        # Note: file_secret_settings is not used but required by pydantic-settings signature
        return (
            init_settings,
            env_settings,
            YamlConfigSettingsSource(settings_cls),
            dotenv_settings,
        )
