"""
Runtime configuration, read from the environment.

Settings are loaded from an injectable mapping rather than reaching into
os.environ directly, so tests can exercise every combination without patching
global state.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Mapping
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Local development hosts the studio and the API on the same origin, so the
# browser never issues a cross-origin request against these defaults.
DEFAULT_CORS_ORIGINS: tuple[str, ...] = (
    "http://127.0.0.1:8015",
    "http://localhost:8015",
)

WILDCARD = "*"

_TRUTHY = {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    """Effective runtime settings for the gateway."""

    environment: str = "development"
    cors_origins: tuple[str, ...] = DEFAULT_CORS_ORIGINS
    cors_allow_credentials: bool = False
    log_level: str = "INFO"
    log_health_probes: bool = False

    @property
    def allows_any_origin(self) -> bool:
        return WILDCARD in self.cors_origins


def _parse_bool(raw: str | None, default: bool = False) -> bool:
    if raw is None:
        return default
    return raw.strip().lower() in _TRUTHY


def _parse_origins(raw: str | None) -> tuple[str, ...]:
    if raw is None:
        return DEFAULT_CORS_ORIGINS
    origins = tuple(item.strip() for item in raw.split(",") if item.strip())
    return origins or DEFAULT_CORS_ORIGINS


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    """
    Build Settings from environment variables.

    Recognised keys, all prefixed ACCESSAI_:
        ENVIRONMENT, CORS_ORIGINS, CORS_ALLOW_CREDENTIALS, LOG_LEVEL,
        LOG_HEALTH_PROBES

    ENVIRONMENT is also honoured unprefixed, because the shipped compose file
    sets it that way.
    """
    source: Mapping[str, str] = os.environ if env is None else env

    environment = source.get("ACCESSAI_ENVIRONMENT") or source.get("ENVIRONMENT") or "development"
    origins = _parse_origins(source.get("ACCESSAI_CORS_ORIGINS"))
    allow_credentials = _parse_bool(source.get("ACCESSAI_CORS_ALLOW_CREDENTIALS"))

    # The Fetch specification forbids pairing a wildcard origin with credentials:
    # a browser rejects the response outright, so the combination silently breaks
    # every credentialed cross-origin call. Refuse to build it.
    if WILDCARD in origins and allow_credentials:
        logger.warning(
            "ACCESSAI_CORS_ALLOW_CREDENTIALS was requested with a wildcard origin. "
            "Browsers reject that pair, so credentials are disabled. "
            "List explicit origins in ACCESSAI_CORS_ORIGINS to send credentials."
        )
        allow_credentials = False

    return Settings(
        environment=environment,
        cors_origins=origins,
        cors_allow_credentials=allow_credentials,
        log_level=(source.get("ACCESSAI_LOG_LEVEL") or "INFO").upper(),
        log_health_probes=_parse_bool(source.get("ACCESSAI_LOG_HEALTH_PROBES")),
    )


def configure_logging(level: str = "INFO") -> None:
    """
    Install a single stream handler with a consistent format.

    force=True replaces any handler uvicorn or a previous call already installed,
    so log lines do not appear twice when the app is reloaded.
    """
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s %(levelname)-8s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        force=True,
    )
