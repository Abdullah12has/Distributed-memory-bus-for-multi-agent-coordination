"""Runtime configuration.

A single :class:`M6Settings` Pydantic model is the source of truth. Values are
resolved in the following order (later wins):

1. ``.env`` (loaded via ``python-dotenv``).
2. Process environment.
3. CLI ``--key=value`` overrides applied with :func:`override`.

The module exposes :func:`get_settings` which returns a frozen
``functools.lru_cache``-d instance. Production code should call ``get_settings()``;
tests should call :func:`reset_settings_cache` followed by environment mutation.

Reference: ``docs/TECHNICAL_REFERENCE.md`` §6.5 (configuration sources of truth)
and ``.env.example``.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

EnvName = Literal["dev", "test", "prod"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
LogFormat = Literal["json", "console"]
InferenceBackendName = Literal["mlx", "ollama", "llamacpp", "openai", "anthropic"]
CompressorName = Literal["icae", "icae-tag", "lingua2", "filter", "none"]


class M6Settings(BaseSettings):  # type: ignore[misc]
    """Resolved runtime configuration for every entry-point in the project.

    Values map 1-1 to the variables documented in ``.env.example``. Subsystems
    receive a strongly-typed ``M6Settings`` rather than reading ``os.environ``
    directly — this keeps the surface auditable.
    """

    model_config = SettingsConfigDict(
        env_prefix="M6_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        frozen=True,
    )

    # ----- service ----------------------------------------------------------
    env: EnvName = "dev"
    host: str = "0.0.0.0"
    port: int = 8080
    log_level: LogLevel = "INFO"
    log_format: LogFormat = "json"

    # ----- storage ----------------------------------------------------------
    db_path: Path = Field(default_factory=lambda: Path("./data/audit.sqlite"))
    faiss_path: Path = Field(default_factory=lambda: Path("./data/index.faiss"))
    scratchpad_ttl_seconds: int = 3600

    # ----- compressor defaults ----------------------------------------------
    default_compressor: CompressorName = "icae"
    default_ratio: float = 4.0
    default_tag_head: bool = False

    # ----- inference defaults -----------------------------------------------
    inference_backend: InferenceBackendName = "mlx"
    default_model: str = "llama-3.1-8b-instruct"

    # ----- external APIs ----------------------------------------------------
    openai_api_key: SecretStr | None = Field(default=None, validation_alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", validation_alias="OPENAI_MODEL")
    anthropic_api_key: SecretStr | None = Field(default=None, validation_alias="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-haiku-4-5", validation_alias="ANTHROPIC_MODEL")
    anthropic_crosscheck_model: str = Field(
        default="claude-sonnet-4-6", validation_alias="ANTHROPIC_CROSSCHECK_MODEL"
    )

    # ----- HF cache ---------------------------------------------------------
    hf_token: SecretStr | None = Field(default=None, validation_alias="HF_TOKEN")
    hf_home: Path = Field(
        default_factory=lambda: Path("./data/hf-cache"), validation_alias="HF_HOME"
    )

    # ----- experiment defaults ---------------------------------------------
    default_seeds: Annotated[tuple[int, ...], Field(default=(0, 1, 2, 3, 4))]
    results_dir: Path = Field(default_factory=lambda: Path("./results"))

    # ----- observability ----------------------------------------------------
    otel_service_name: str = Field(default="m6-memory-bus", validation_alias="OTEL_SERVICE_NAME")
    otel_exporter_otlp_endpoint: str = Field(
        default="", validation_alias="OTEL_EXPORTER_OTLP_ENDPOINT"
    )

    # ------------------------------------------------------------------ #
    # Validators
    # ------------------------------------------------------------------ #
    @field_validator("default_seeds", mode="before")
    @classmethod
    def _parse_seeds(cls, value: object) -> tuple[int, ...]:
        """Accept ``"0,1,2"`` from env. Empty string ⇒ default."""
        if value is None or value == "":
            return (0, 1, 2, 3, 4)
        if isinstance(value, list | tuple):
            return tuple(int(v) for v in value)
        if isinstance(value, str):
            return tuple(int(x.strip()) for x in value.split(",") if x.strip())
        msg = f"Cannot parse default_seeds={value!r}"
        raise ValueError(msg)

    @field_validator("default_ratio")
    @classmethod
    def _check_ratio(cls, value: float) -> float:
        if not 1.0 <= value <= 32.0:
            msg = f"default_ratio must be in [1, 32], got {value}"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def _resolve_paths(self) -> M6Settings:
        # We do NOT auto-create directories here: doing so on import would race
        # with tests. Subsystems that need a path call ``settings.ensure(...)``.
        return self

    # ------------------------------------------------------------------ #
    # Convenience methods
    # ------------------------------------------------------------------ #
    def ensure(self, path: Path) -> Path:
        """Create the parent directory if missing; return the path."""
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def has_openai(self) -> bool:
        return self.openai_api_key is not None and self.openai_api_key.get_secret_value() != ""

    def has_anthropic(self) -> bool:
        return (
            self.anthropic_api_key is not None and self.anthropic_api_key.get_secret_value() != ""
        )


@lru_cache(maxsize=1)
def get_settings() -> M6Settings:
    """Return the process-wide :class:`M6Settings` instance.

    Cached because most call sites resolve settings hundreds of times per
    request. Use :func:`reset_settings_cache` in tests.
    """
    return M6Settings()


def reset_settings_cache() -> None:
    """Clear the :func:`get_settings` cache (test-only)."""
    get_settings.cache_clear()


def override(**kwargs: object) -> M6Settings:
    """Build a settings instance with ad-hoc overrides.

    Intended for CLI integration: parse ``--key value`` pairs into ``kwargs``
    and pass them here. The base settings are loaded from env as usual; the
    overrides take precedence.
    """
    base_settings = M6Settings()
    base = base_settings.model_dump()
    base.update(kwargs)
    return M6Settings(**base)


def project_root() -> Path:
    """Return the repo root.

    Two-step lookup so it works whether the package is installed editable or
    via a wheel: walk up from this file until we find ``pyproject.toml``.
    Falls back to ``cwd`` if the marker is missing.
    """
    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    return Path(os.getcwd()).resolve()
